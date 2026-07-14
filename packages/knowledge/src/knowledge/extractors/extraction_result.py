from dataclasses import dataclass
from datetime import datetime

from knowledge.graph import KnowledgeGraph


@dataclass(frozen=True, kw_only=True)
class KnowledgeExtractionResult:
    """Immutable record of a completed knowledge extraction operation."""
    
    graph: KnowledgeGraph
    extractor_id: str
    extractor_name: str
    version: str
    processing_time_ms: float
    processed_chunks: int
    created_at: datetime
