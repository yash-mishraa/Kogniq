from dataclasses import dataclass

from knowledge.enums import RelationshipType
from knowledge.exceptions import InvalidRelationshipError
from knowledge.metadata import KnowledgeMetadata


@dataclass(frozen=True, kw_only=True)
class KnowledgeRelationship:
    """An immutable relationship between two knowledge concepts."""
    
    id: str
    source_concept: str
    target_concept: str
    relationship_type: RelationshipType
    confidence: float
    metadata: KnowledgeMetadata

    def __post_init__(self) -> None:
        if self.source_concept == self.target_concept:
            raise InvalidRelationshipError(
                "Source and target concepts cannot be the same."
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise InvalidRelationshipError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
