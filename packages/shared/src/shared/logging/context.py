"""Context propagation for standard-library log records."""

from collections.abc import Mapping, MutableMapping
from contextvars import ContextVar
from logging import Filter, Logger, LoggerAdapter, LogRecord, getLogger
from typing import Any

_telemetry_context: ContextVar[Mapping[str, object]] = ContextVar("telemetry_context")

def get_telemetry_context() -> Mapping[str, object]:
    """Get the current telemetry context."""
    return _telemetry_context.get({})

def set_telemetry_context(context: Mapping[str, object]) -> Any:
    """Set the telemetry context and return the token."""
    return _telemetry_context.set(context)

def update_telemetry_context(**kwargs: object) -> None:
    """Update the current telemetry context."""
    current = dict(_telemetry_context.get({}))
    current.update(kwargs)
    _telemetry_context.set(current)

def reset_telemetry_context(token: Any) -> None:
    """Reset the telemetry context using a token."""
    _telemetry_context.reset(token)

class TelemetryContextFilter(Filter):
    """Inject telemetry context into log records."""
    def filter(self, record: LogRecord) -> bool:
        ctx = get_telemetry_context()
        for k, v in ctx.items():
            if not hasattr(record, k):
                setattr(record, k, v)
        return True


class ContextLoggerAdapter(LoggerAdapter[Logger]):
    """Attach stable, non-sensitive context to every emitted log record."""

    def process(
        self,
        msg: object,
        kwargs: MutableMapping[str, Any],
    ) -> tuple[object, MutableMapping[str, Any]]:
        extra = dict(self.extra or {})
        supplied_extra = kwargs.get("extra")
        if isinstance(supplied_extra, Mapping):
            extra.update(supplied_extra)
        kwargs["extra"] = extra
        return msg, kwargs


def get_context_logger(
    name: str,
    context: Mapping[str, object] | None = None,
) -> ContextLoggerAdapter:
    """Return a logger adapter with caller-supplied contextual fields."""
    return ContextLoggerAdapter(getLogger(name), dict(context or {}))

