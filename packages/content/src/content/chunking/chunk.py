from dataclasses import dataclass
from datetime import datetime

from ..normalized.validation import validate_non_negative, validate_not_empty
from .exceptions import InvalidChunkError
from .metadata import ChunkMetadata
from .statistics import ChunkStatistics


@dataclass(frozen=True, kw_only=True)
class Chunk:
    """An immutable chunk of text extracted from a NormalizedDocument."""
    
    id: str
    document_id: str
    chunk_index: int
    text: str
    
    title: str | None = None
    page_number: int | None = None
    section_title: str | None = None
    
    metadata: ChunkMetadata
    statistics: ChunkStatistics
    created_at: datetime
    
    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id", InvalidChunkError)
        validate_not_empty(self.document_id, "document_id", InvalidChunkError)
        validate_not_empty(self.text, "text", InvalidChunkError)
        
        validate_non_negative(self.chunk_index, "chunk_index", InvalidChunkError)
