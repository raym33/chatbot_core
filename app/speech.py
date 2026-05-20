from __future__ import annotations

import asyncio
import io
import wave

import edge_tts
import numpy as np
import whisper

from app.config import Settings


class SpeechService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.whisper_cache_dir.mkdir(parents=True, exist_ok=True)
        self.settings.speech_temp_dir.mkdir(parents=True, exist_ok=True)
        self._model = None

    async def synthesize(self, text: str) -> bytes:
        clean = " ".join(text.strip().split())
        if not clean:
            raise ValueError("Texto vacio para sintesis")
        communicate = edge_tts.Communicate(
            text=clean[:1500],
            voice=self.settings.edge_tts_voice,
            rate=self.settings.edge_tts_rate,
        )
        chunks: list[bytes] = []
        async for item in communicate.stream():
            if item["type"] == "audio":
                chunks.append(item["data"])
        return b"".join(chunks)

    async def transcribe_wav_bytes(self, raw: bytes) -> str:
        return await asyncio.to_thread(self._transcribe_wav_bytes_sync, raw)

    def _transcribe_wav_bytes_sync(self, raw: bytes) -> str:
        audio = _wav_bytes_to_float32(raw, self.settings.whisper_sample_rate)
        model = self._load_model()
        result = model.transcribe(
            audio,
            language=self.settings.whisper_language,
            fp16=False,
            verbose=False,
            task="transcribe",
            temperature=0.0,
        )
        return str(result.get("text", "")).strip()

    def _load_model(self):
        if self._model is None:
            self._model = whisper.load_model(
                self.settings.whisper_model_name,
                download_root=str(self.settings.whisper_cache_dir),
            )
        return self._model


def _wav_bytes_to_float32(raw: bytes, target_sample_rate: int) -> np.ndarray:
    with wave.open(io.BytesIO(raw), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        frames = wav_file.readframes(frame_count)

    if not frames:
        raise ValueError("Audio vacio")

    if sample_width == 1:
        audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sample_width == 2:
        audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Formato WAV no soportado: {sample_width * 8} bits")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    if sample_rate != target_sample_rate:
        audio = _resample_audio(audio, sample_rate, target_sample_rate)

    return np.clip(audio.astype(np.float32), -1.0, 1.0)


def _resample_audio(audio: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
    if original_rate == target_rate:
        return audio
    duration = len(audio) / float(original_rate)
    target_length = max(1, int(duration * target_rate))
    source_positions = np.linspace(0.0, len(audio) - 1, num=len(audio), dtype=np.float32)
    target_positions = np.linspace(0.0, len(audio) - 1, num=target_length, dtype=np.float32)
    return np.interp(target_positions, source_positions, audio).astype(np.float32)
