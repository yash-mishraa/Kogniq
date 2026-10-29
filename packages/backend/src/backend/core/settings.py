from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendConfig(BaseSettings):
    """
    Core application configuration, driven by environment variables.
    """

    # Database Settings
    chroma_db_path: str = "./data/chroma"
    # The legacy ``kogniq`` collection was found to contain a corrupted HNSW
    # index (nearest-neighbour results disagreed with brute-force cosine
    # similarity). New writes go to a versioned collection so a rebuild is
    # explicit and auditable rather than silently mixing index generations.
    chroma_collection: str = "kogniq_v2"
    vector_store_provider: Literal["memory", "chroma", "qdrant"] = "chroma"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "kogniq_documents"
    persistence_provider: Literal["memory", "sqlite"] = "sqlite"
    sqlite_database_path: str = "./data/kogniq.db"
    knowledge_extraction_provider: Literal["fake", "gemini", "local", "auto"] = "auto"
    learning_generation_provider: Literal[
        "fake", "mock", "gemini", "deterministic-fake", "local", "ollama", "auto"
    ] = "auto"
    local_llm_url: str = "http://localhost:11434"
    local_llm_model: str = "llama3.2:3b"
    gemini_model: str = "gemini-3.5-flash-lite"
    provider_fallback_enabled: bool = True

    @field_validator("gemini_model", mode="before")
    @classmethod
    def _normalize_gemini_model(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean in (
                "gemini-2.5-flash",
                "gemini-1.5-flash",
                "gemini-2.0-flash",
                "gemini-2.5-flash-lite",
                "gemini-flash",
            ):
                return "gemini-3.5-flash-lite"
            return v_clean
        return v

    @field_validator("learning_generation_provider", mode="before")
    @classmethod
    def _normalize_learning_provider(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean.startswith("gemi"):
                return "gemini"
            return v_clean
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Kogniq API"
    version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "testing", "production"] = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["*"]
    similarity_threshold: float = 0.35


# Expose a default instance for easy access
settings = BackendConfig()
