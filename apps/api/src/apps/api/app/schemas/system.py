"""System endpoint response schemas."""

from typing import Literal

from pydantic import BaseModel, Field

from shared.config import Environment


class HealthResponse(BaseModel):
    """Current process health and lifecycle metadata."""

    status: Literal["ok"]
    version: str
    environment: Environment
    uptime_seconds: float = Field(ge=0)
    application: str


class VersionResponse(BaseModel):
    """Application and build version metadata."""

    application: str
    version: str
    build: str
    commit: str
    api_version: str
