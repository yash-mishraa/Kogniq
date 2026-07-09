from dataclasses import dataclass

from .enums import RelationshipType
from .exceptions import InvalidRelationshipError, validate_not_empty


@dataclass(frozen=True, kw_only=True)
class EducationalRelationship:
    """Connects two educational entities."""

    source_id: str
    target_id: str
    relationship_type: RelationshipType

    def __post_init__(self) -> None:
        validate_not_empty(self.source_id, "source_id", InvalidRelationshipError)
        validate_not_empty(self.target_id, "target_id", InvalidRelationshipError)
        if self.source_id == self.target_id:
            raise InvalidRelationshipError("Source and target IDs cannot be identical.")
