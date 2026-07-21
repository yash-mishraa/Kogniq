from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessDocumentResult:
    status: str
    document_id: str
    filename: str
    processor: str
    chunk_count: int
    embedding_count: int
    knowledge_concepts: int
    knowledge_relationships: int
    processing_time_ms: float
    warnings: Sequence[str]
