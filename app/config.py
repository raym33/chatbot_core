from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MUNIBOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Chatbot Core"
    host: str = "0.0.0.0"
    port: int = 8000
    city_name: str = "Example Organization"
    organization_name: str = "Chatbot Core Demo"
    organization_type: str = "company"
    domain_profile_path: Path | None = BASE_DIR / "profiles" / "company.json"
    public_base_url: str = "http://localhost:8000"
    db_path: Path = BASE_DIR / "data" / "munibot.sqlite3"
    corpus_dir: Path = BASE_DIR / "data" / "corpus"
    rag_index_path: Path = BASE_DIR / "data" / "rag_index.json"
    demo_backend_dir: Path = BASE_DIR / "data" / "demo_backend"
    document_intake_dir: Path = BASE_DIR / "data" / "document_intake"
    ocr_output_dir: Path = BASE_DIR / "data" / "ocr_outputs"
    allowed_origins_raw: str = "http://localhost:8000,http://127.0.0.1:8000"
    ai_backend: str = "lmstudio"
    lmstudio_base_url: str = "http://127.0.0.1:1234"
    lmstudio_chat_model: str = "gemma-4-26b-a4b-it-mlx"
    lmstudio_embed_model: str = "text-embedding-nomic-embed-text-v1.5"
    ollama_hosts_raw: str = "http://127.0.0.1:11434"
    ollama_chat_model: str = "qwen3.5:9b"
    ollama_embed_model: str = "nomic-embed-text"
    llm_timeout_seconds: float = 60.0
    session_ttl_minutes: int = 120
    appointment_url: str = "https://example.com/appointments"
    incidents_url: str = "https://example.com/support/incidents"
    human_handoff_url: str = "https://example.com/support/contact"
    widget_accent: str = "#0A4A73"
    widget_title: str = "Assistant"
    easy_read_max_sentences: int = 3
    top_k: int = 5
    lexical_weight: float = 0.45
    semantic_weight: float = 0.55
    enable_semantic_rag: bool = True
    enable_answer_verification: bool = True
    min_grounding_score: float = 0.18
    golden_set_path: Path = BASE_DIR / "datasets" / "evaluation" / "golden_general_es.jsonl"
    max_message_chars: int = 4000
    request_body_limit_bytes: int = 4_000_000
    requests_per_minute: int = 90
    strict_domain_guard: bool = False
    redact_pii: bool = True
    retain_conversations_days: int = 30
    retain_escalations_days: int = 90
    edge_tts_voice: str = "en-US-AriaNeural"
    edge_tts_rate: str = "+0%"
    whisper_model_name: str = "base"
    whisper_language: str = "en"
    whisper_sample_rate: int = 16_000
    whisper_cache_dir: Path = BASE_DIR / "data" / "whisper_models"
    speech_temp_dir: Path = BASE_DIR / "data" / "speech_temp"

    @property
    def allowed_origins(self) -> list[str]:
        return [value.strip() for value in self.allowed_origins_raw.split(",") if value.strip()]

    @property
    def ollama_hosts(self) -> list[str]:
        return [value.strip().rstrip("/") for value in self.ollama_hosts_raw.split(",") if value.strip()]

    @property
    def chat_model(self) -> str:
        if self.ai_backend == "lmstudio":
            return self.lmstudio_chat_model
        return self.ollama_chat_model

    @property
    def embed_model(self) -> str:
        if self.ai_backend == "lmstudio":
            return self.lmstudio_embed_model
        return self.ollama_embed_model

    @property
    def effective_organization_name(self) -> str:
        if self.organization_name != "Chatbot Core Demo":
            return self.organization_name
        return self.city_name


@lru_cache
def get_settings() -> Settings:
    return Settings()
