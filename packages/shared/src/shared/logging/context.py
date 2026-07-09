"""Context propagation for standard-library log records."""

from collections.abc import Mapping, MutableMapping
from logging import Logger, LoggerAdapter, getLogger
from typing import Any


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
