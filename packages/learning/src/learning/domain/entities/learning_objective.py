from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import AIMetadata, ConceptId, LearningObjectiveId, generate_id


@dataclass
class LearningObjective:
    """
    Entity representing a measurable goal or outcome for a learner.
    Invariant: Must reference exactly one Concept.
    """

    concept_id: ConceptId
    description: str
    id: LearningObjectiveId = field(default_factory=lambda: LearningObjectiveId(generate_id()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise ValueError("Learning objective description cannot be empty.")
        if self.concept_id is None:
            raise ValueError(
                "Learning objective must reference a Concept (concept_id cannot be None)."
            )
