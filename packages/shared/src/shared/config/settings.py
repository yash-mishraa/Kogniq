"""Immutable settings shared by future application composition roots."""

from dataclasses import dataclass

from shared.config.constants import DEFAULT_LOG_LEVEL
from shared.config.environment import Environment


@dataclass(frozen=True, slots=True)
class Settings:
    """Minimal provider-neutral settings with safe defaults."""

    environment: Environment = Environment.LOCAL
    log_level: str = DEFAULT_LOG_LEVEL
