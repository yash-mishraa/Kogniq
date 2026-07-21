import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class DomainEncoder(json.JSONEncoder):
    """Custom JSON encoder for domain models."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.name
        if is_dataclass(obj):
            return asdict(obj)  # type: ignore
        return super().default(obj)


def serialize(obj: Any) -> str:
    """Serialize a domain object or primitive to a JSON string."""
    if obj is None:
        return "{}"
    return json.dumps(obj, cls=DomainEncoder)


def deserialize(data: str | None) -> Any:
    """Deserialize a JSON string to a dictionary or primitive."""
    if not data:
        return {}
    return json.loads(data)
