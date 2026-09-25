"""Central standard-library logging configuration."""

import json
from dataclasses import dataclass
from logging import Formatter, LogRecord, getLevelNamesMapping
from logging.config import dictConfig
from threading import Lock
from typing import Any, Final

from shared.config.constants import DEFAULT_LOG_LEVEL
from shared.exceptions import InvalidConfigurationError

DEFAULT_LOG_FORMAT: Final = "%(asctime)s %(levelname)s %(name)s %(message)s"
_configuration_lock = Lock()
_is_configured = False


class JSONFormatter(Formatter):
    """Format log records as single-line JSON."""

    def format(self, record: LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "event": record.getMessage(),
            "name": record.name,
        }

        # Pull extra attributes
        exclude = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module", "msecs",
            "message", "msg", "name", "pathname", "process", "processName",
            "relativeCreated", "stack_info", "thread", "threadName", "taskName",
        }

        for k, v in record.__dict__.items():
            if k not in exclude:
                try:
                    # quick check for valid json serialization
                    json.dumps(v)
                    payload[k] = v
                except (TypeError, ValueError):
                    payload[k] = str(v)

        return json.dumps(payload, default=str)


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Inputs for process-wide standard-library logging setup."""

    level: str = DEFAULT_LOG_LEVEL
    message_format: str = DEFAULT_LOG_FORMAT
    format_type: str = "TEXT"


def configure_logging(config: LoggingConfig | None = None) -> None:
    """Configure process logging exactly once without provider dependencies."""
    global _is_configured

    effective_config = config or LoggingConfig()
    level = effective_config.level.upper()
    if level not in getLevelNamesMapping():
        raise InvalidConfigurationError(
            f"Unsupported logging level: {effective_config.level!r}.",
        )
    
    fmt_type = effective_config.format_type.upper()
    if fmt_type not in ("TEXT", "JSON"):
        fmt_type = "TEXT"

    with _configuration_lock:
        if _is_configured:
            return
            
        formatter_class = (
            "shared.logging.configuration.JSONFormatter"
            if fmt_type == "JSON"
            else "logging.Formatter"
        )

        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "()": formatter_class,
                        "format": effective_config.message_format,
                    },
                },
                "filters": {
                    "telemetry_filter": {
                        "()": "shared.logging.context.TelemetryContextFilter",
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                        "level": level,
                        "stream": "ext://sys.stdout",
                        "filters": ["telemetry_filter"],
                    },
                },
                "root": {
                    "handlers": ["console"],
                    "level": level,
                },
            },
        )
        _is_configured = True
