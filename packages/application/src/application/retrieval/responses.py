from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ChunkData:
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalResult:
    status: str
    query: str
    document_id: str
    total_results: int
    results: Sequence[ChunkData]
    processing_time_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)
