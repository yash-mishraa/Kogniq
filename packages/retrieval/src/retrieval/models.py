import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class RetrievalQuery:
    """
    Immutable representation of a retrieval query.
    Defines the exact text to search for, the desired limit, and optional filtering metadata.
    """
    text: str
    top_k: int = 10
    query_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    filters: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """
    Immutable representation of a retrieved item.
    Abstracts away the Vector Store response to expose only the retrieval
    context and chunk reference. Actual Chunk hydration is deferred to a future repository layer.
    """
    query_id: str
    query_text: str
    embedding_id: str
    chunk_id: str
    similarity_score: float
    provider: str
    model: str
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))
