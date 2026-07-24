from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessDocumentResult:
    status: str
    document_id: str
    filename: str
    title: str
    source: str
    processor: str
    chunk_count: int
    processing_time_ms: float
    warnings: Sequence[str]
