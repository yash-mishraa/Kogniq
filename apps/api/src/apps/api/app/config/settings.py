"""Environment-driven settings for the Kogniq API application."""

from importlib.metadata import PackageNotFoundError, version

from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.config import Environment
from shared.config.constants import DEFAULT_LOG_LEVEL


def _distribution_version() -> str:
    try:
        return version("kogniq-api")
    except PackageNotFoundError:
        return "0.0.0"


class OpenAPIServer(BaseModel):
    """One server entry exposed in the OpenAPI document."""

    url: str
    description: str


class APISettings(BaseSettings):
    """Validated API configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="KOGNIQ_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    app_name: str = "Kogniq API"
    app_version: str = Field(default_factory=_distribution_version)
    api_version: str = "v1"
    environment: Environment = Environment.DEVELOPMENT
    build: str = "local"
    commit: str = "unknown"
    log_level: str = DEFAULT_LOG_LEVEL
    log_format: str = "TEXT"

    cors_origins: list[str] | str = Field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    allowed_hosts: list[str] | str = Field(
        default_factory=lambda: ["*"],
    )

    @field_validator("allowed_hosts", "cors_origins", mode="after")
    @classmethod
    def _parse_list_fields(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("[") and v_clean.endswith("]"):
                import json
                try:
                    return json.loads(v_clean)
                except Exception:
                    pass
            return [part.strip() for part in v_clean.split(",") if part.strip()]
        return v
    gzip_enabled: bool = True
    gzip_minimum_size: int = Field(default=500, ge=0)
    request_id_header: str = "X-Request-ID"
    process_time_header: str = "X-Process-Time-Ms"

    # Session Configuration
    session_cookie_name: str = "kogniq_session"
    session_cookie_max_age: int = 86400  # 24 hours
    session_cookie_secure: bool = False  # Set to true in prod

    openapi_description: str = (
        "Foundational application API for the Kogniq AI Learning Intelligence Platform."
    )
    openapi_tags: list[dict[str, str]] = Field(
        default_factory=lambda: [
            {
                "name": "system",
                "description": "Application health and build metadata.",
            },
        ],
    )
    openapi_servers: list[OpenAPIServer] = Field(
        default_factory=lambda: [
            OpenAPIServer(url="/", description="Current environment"),
        ],
    )
    contact_name: str = "Yash Mishra"
    contact_url: str | None = "https://github.com/yash-mishraa"
    contact_email: str | None = None
    license_name: str | None = None
    license_url: str | None = None
