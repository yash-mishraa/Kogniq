from dataclasses import dataclass
from datetime import datetime

from .metadata import EmbeddingMetadata
from .statistics import EmbeddingStatistics
from .vector import EmbeddingVector


@dataclass(frozen=True, slots=True)
class Embedding:
    """Immutable representation of a generated chunk embedding."""

    id: str
    chunk_id: str
    vector: EmbeddingVector
    metadata: EmbeddingMetadata
    statistics: EmbeddingStatistics
    created_at: datetime
