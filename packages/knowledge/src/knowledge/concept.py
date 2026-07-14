from dataclasses import dataclass

from knowledge.enums import ConceptType
from knowledge.exceptions import InvalidConceptError
from knowledge.metadata import KnowledgeMetadata


@dataclass(frozen=True, kw_only=True)
class KnowledgeConcept:
    """An immutable educational concept."""
    
    id: str
    title: str
    description: str
    concept_type: ConceptType
    aliases: tuple[str, ...]
    metadata: KnowledgeMetadata

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidConceptError("Concept title cannot be empty.")
        if not isinstance(self.aliases, tuple):
            raise InvalidConceptError("Aliases must be an immutable tuple.")
