from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendConfig(BaseSettings):
    """
    Core application configuration, driven by environment variables.
    """

    # Database Settings
    chroma_db_path: str = "./data/chroma"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Kogniq API"
    version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "testing", "production"] = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["*"]


# Expose a default instance for easy access
settings = BackendConfig()
