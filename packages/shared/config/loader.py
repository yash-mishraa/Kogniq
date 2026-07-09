"""Environment-backed implementation of the generic settings provider."""

from collections.abc import Mapping
from os import environ

from shared.config.constants import (
    DEFAULT_ENV_PREFIX,
    DEFAULT_LOG_LEVEL,
    SUPPORTED_LOG_LEVELS,
)
from shared.config.environment import Environment
from shared.config.settings import Settings
from shared.exceptions import InvalidConfigurationError
from shared.interfaces.configuration import SettingsProvider


class EnvironmentSettingsProvider(SettingsProvider[Settings]):
    """Load minimal settings from an injected environment mapping."""

    def __init__(
        self,
        values: Mapping[str, str] | None = None,
        prefix: str = DEFAULT_ENV_PREFIX,
    ) -> None:
        self._values = environ if values is None else values
        self._prefix = prefix

    def load(self) -> Settings:
        """Build validated immutable settings."""
        environment_value = self._get("ENVIRONMENT", Environment.LOCAL.value)
        log_level = self._get("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()

        try:
            environment = Environment(environment_value.lower())
        except ValueError as error:
            supported = ", ".join(item.value for item in Environment)
            raise InvalidConfigurationError(
                f"Unsupported environment {environment_value!r}; expected one of: {supported}.",
            ) from error

        if log_level not in SUPPORTED_LOG_LEVELS:
            supported = ", ".join(sorted(SUPPORTED_LOG_LEVELS))
            raise InvalidConfigurationError(
                f"Unsupported log level {log_level!r}; expected one of: {supported}.",
            )

        return Settings(environment=environment, log_level=log_level)

    def _get(self, name: str, default: str) -> str:
        return self._values.get(f"{self._prefix}{name}", default)

