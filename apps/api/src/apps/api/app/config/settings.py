"""Environment-driven settings for the Kogniq API application."""

from importlib.metadata import PackageNotFoundError, version

from pydantic import BaseModel, Field
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

    cors_origins: list[str] = Field(default_factory=list)
    cors_allow_credentials: bool = False
    allowed_hosts: list[str] = Field(
        default_factory=lambda: ["127.0.0.1", "localhost", "testserver"],
    )
    gzip_enabled: bool = True
    gzip_minimum_size: int = Field(default=500, ge=0)
    request_id_header: str = "X-Request-ID"
    process_time_header: str = "X-Process-Time-Ms"

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
