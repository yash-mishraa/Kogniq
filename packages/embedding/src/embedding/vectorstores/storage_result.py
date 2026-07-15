from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StorageResult:
    """Result of a storage operation in a vector store."""
    stored_count: int
    collection_name: str
    metadata: dict[str, Any] | None = None
