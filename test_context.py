from contextvars import ContextVar
from typing import Mapping

_telemetry_context: ContextVar[Mapping[str, object]] = ContextVar("telemetry_context", default={})

def get_telemetry_context() -> Mapping[str, object]:
    return _telemetry_context.get()

def set_telemetry_context(context: Mapping[str, object]) -> None:
    _telemetry_context.set(context)

def update_telemetry_context(**kwargs: object) -> None:
    current = dict(_telemetry_context.get())
    current.update(kwargs)
    _telemetry_context.set(current)
