from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmbeddingStatistics:
    """Represents generation statistics only, completely disconnected from retrieval metrics."""
    
    processing_time_ms: float
    token_count: int | None = None
    batch_size: int | None = None
    memory_bytes: int | None = None
