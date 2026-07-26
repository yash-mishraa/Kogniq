import hashlib
from dataclasses import dataclass
from datetime import datetime

from knowledge.enums import ConceptType
from knowledge.exceptions import InvalidConceptError
from knowledge.metadata import KnowledgeMetadata


@dataclass(frozen=True, kw_only=True)
class KnowledgeConcept:
    """An immutable educational concept."""

    id: str
    document_id: str
    name: str
    description: str
    concept_type: ConceptType
    aliases: tuple[str, ...]
    confidence: float
    created_at: datetime
    metadata: KnowledgeMetadata

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidConceptError("Concept name cannot be empty.")
        if not isinstance(self.aliases, tuple):
            raise InvalidConceptError("Aliases must be an immutable tuple.")
        if not (0.0 <= self.confidence <= 1.0):
            raise InvalidConceptError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )

    @staticmethod
    def generate_id(document_id: str, name: str) -> str:
        """Generates a stable, deterministic ID for a concept within a document."""
        normalized_name = name.strip().lower()
        key = f"{document_id}:{normalized_name}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()
