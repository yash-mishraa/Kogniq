from dataclasses import dataclass
from datetime import datetime

from ..normalized.validation import validate_non_negative
from .exceptions import InvalidChunkError


@dataclass(frozen=True, kw_only=True)
class ChunkStatistics:
    """Statistics purely related to a chunk (no document-level stats)."""
    character_count: int
    line_count: int
    word_count: int
    estimated_tokens: int
    processing_timestamp: datetime
    confidence: float
    
    def __post_init__(self) -> None:
        validate_non_negative(self.character_count, "character_count", InvalidChunkError)
        validate_non_negative(self.line_count, "line_count", InvalidChunkError)
        validate_non_negative(self.word_count, "word_count", InvalidChunkError)
        validate_non_negative(self.estimated_tokens, "estimated_tokens", InvalidChunkError)
        
        if not (0.0 <= self.confidence <= 1.0):
            raise InvalidChunkError(
                f"confidence must be between 0.0 and 1.0, got {self.confidence}."
            )
