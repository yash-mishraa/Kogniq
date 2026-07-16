from dataclasses import dataclass
from datetime import datetime

from learning_content.enums import ContentType
from learning_content.exceptions import InvalidLearningContentError
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


@dataclass(frozen=True, kw_only=True)
class LearningContent:
    """Immutable educational content generated from source documents."""
    
    id: str
    source_document_id: str
    source_chunk_ids: tuple[str, ...]
    content_type: ContentType
    title: str
    body: str
    metadata: LearningContentMetadata
    statistics: LearningContentStatistics
    created_at: datetime
    
    def __post_init__(self) -> None:
        if not self.body.strip():
            raise InvalidLearningContentError("Content body cannot be empty")
        if not self.title.strip():
            raise InvalidLearningContentError("Content title cannot be empty")
        if not self.source_chunk_ids:
            raise InvalidLearningContentError("Source chunk IDs must not be empty")
