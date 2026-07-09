from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import AIMetadata, ConceptId, Prerequisite, TopicId, generate_id


@dataclass
class Concept:
    """
    Entity representing an atomic piece of knowledge.
    Invariant: A Concept MUST belong to exactly one Topic.
    """

    topic_id: TopicId
    name: str
    description: str
    id: ConceptId = field(default_factory=lambda: ConceptId(generate_id()))
    prerequisites: list[Prerequisite] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Concept name cannot be empty.")
        if self.topic_id is None:
            raise ValueError("Concept must belong to a Topic (topic_id cannot be None).")

    def add_prerequisite(self, prerequisite: Prerequisite) -> None:
        """Adds a prerequisite, delegating cycle checks to a domain service."""
        if any(
            p.required_concept_id == prerequisite.required_concept_id for p in self.prerequisites
        ):
            return  # Already added
        self.prerequisites.append(prerequisite)
