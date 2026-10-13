from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EmbeddingMetadata:
    """Infrastructure-agnostic metadata about how a vector was generated."""

    provider: str
    model_name: str
    model_version: str
    embedding_version: str
    created_at: datetime
    dimensions: int
    normalized: bool
    language: str | None = None
    document_id: str | None = None
    chunk_hash: str | None = None
    document_checksum: str | None = None
    page_number: int | None = None
    chunk_index: int | None = None
    section_id: str | None = None
    section_title: str | None = None
    section_path: str | None = None
    figure_id: str | None = None
    figure_number: str | None = None
    future_index_name: str | None = None
    future_namespace: str | None = None
