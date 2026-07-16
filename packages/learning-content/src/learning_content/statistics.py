from dataclasses import dataclass

from learning_content.exceptions import InvalidLearningContentError


@dataclass(frozen=True, kw_only=True)
class LearningContentStatistics:
    """Statistics about generated learning content."""
    
    character_count: int
    word_count: int
    estimated_tokens: int
    processing_time_ms: float
    confidence: float
    
    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise InvalidLearningContentError("Confidence must be between 0.0 and 1.0")
        if self.character_count < 0:
            raise InvalidLearningContentError("Character count cannot be negative")
        if self.word_count < 0:
            raise InvalidLearningContentError("Word count cannot be negative")
        if self.estimated_tokens < 0:
            raise InvalidLearningContentError("Estimated tokens cannot be negative")
        if self.processing_time_ms < 0.0:
            raise InvalidLearningContentError("Processing time cannot be negative")
