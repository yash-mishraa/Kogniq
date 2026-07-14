from dataclasses import dataclass

from knowledge.concept import KnowledgeConcept
from knowledge.exceptions import InvalidGraphError
from knowledge.relationship import KnowledgeRelationship


@dataclass(frozen=True, kw_only=True)
class KnowledgeGraph:
    """An immutable collection of concepts and relationships forming a knowledge graph."""
    
    concepts: tuple[KnowledgeConcept, ...]
    relationships: tuple[KnowledgeRelationship, ...]

    def __post_init__(self) -> None:
        concept_ids = set()
        for c in self.concepts:
            if c.id in concept_ids:
                raise InvalidGraphError(f"Duplicate concept id found: {c.id}")
            concept_ids.add(c.id)

        relationship_ids = set()
        for r in self.relationships:
            if r.id in relationship_ids:
                raise InvalidGraphError(f"Duplicate relationship id found: {r.id}")
            relationship_ids.add(r.id)

    @property
    def concept_count(self) -> int:
        return len(self.concepts)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)
