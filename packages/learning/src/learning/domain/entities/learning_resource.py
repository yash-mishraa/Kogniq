from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import (
    AIMetadata,
    ConceptId,
    Difficulty,
    LearningResourceId,
    ResourceReference,
    Tag,
    generate_id,
)


@dataclass
class LearningResource:
    """
    Entity representing educational content (video, text, interactive).
    Invariant: May cover multiple Concepts.
    """

    title: str
    reference: ResourceReference
    id: LearningResourceId = field(default_factory=lambda: LearningResourceId(generate_id()))
    concept_ids: set[ConceptId] = field(default_factory=set)
    difficulty: Difficulty | None = None
    tags: set[Tag] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Learning resource title cannot be empty.")
        if self.reference is None:
            raise ValueError("Learning resource must have a ResourceReference.")
