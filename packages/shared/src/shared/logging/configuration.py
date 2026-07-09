"""Central standard-library logging configuration."""

from dataclasses import dataclass
from logging import getLevelNamesMapping
from logging.config import dictConfig
from threading import Lock
from typing import Final

from shared.config.constants import DEFAULT_LOG_LEVEL
from shared.exceptions import InvalidConfigurationError

DEFAULT_LOG_FORMAT: Final = "%(asctime)s %(levelname)s %(name)s %(message)s"
_configuration_lock = Lock()
_is_configured = False


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Inputs for process-wide standard-library logging setup."""

    level: str = DEFAULT_LOG_LEVEL
    message_format: str = DEFAULT_LOG_FORMAT


def configure_logging(config: LoggingConfig | None = None) -> None:
    """Configure process logging exactly once without provider dependencies."""
    global _is_configured

    effective_config = config or LoggingConfig()
    level = effective_config.level.upper()
    if level not in getLevelNamesMapping():
        raise InvalidConfigurationError(
            f"Unsupported logging level: {effective_config.level!r}.",
        )

    with _configuration_lock:
        if _is_configured:
            return

        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": effective_config.message_format,
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                        "level": level,
                        "stream": "ext://sys.stdout",
                    },
                },
                "root": {
                    "handlers": ["console"],
                    "level": level,
                },
            },
        )
        _is_configured = True
