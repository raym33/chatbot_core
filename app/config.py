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

    app_name: str = "Munibot Local"
    host: str = "0.0.0.0"
    port: int = 8000
    city_name: str = "Ayuntamiento de Murcia"
    public_base_url: str = "http://localhost:8000"
    db_path: Path = BASE_DIR / "data" / "munibot.sqlite3"
    corpus_dir: Path = BASE_DIR / "data" / "corpus"
    rag_index_path: Path = BASE_DIR / "data" / "rag_index.json"
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
    appointment_url: str = "https://www.murcia.es/web/guest/cita-previa"
    incidents_url: str = "https://www.murcia.es/web/guest/incidencias"
    human_handoff_url: str = "https://www.murcia.es/web/guest/atencion-ciudadana"
    widget_accent: str = "#0A4A73"
    widget_title: str = "Asistente municipal"
    easy_read_max_sentences: int = 3
    top_k: int = 5
    lexical_weight: float = 0.45
    semantic_weight: float = 0.55
    enable_semantic_rag: bool = True

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
