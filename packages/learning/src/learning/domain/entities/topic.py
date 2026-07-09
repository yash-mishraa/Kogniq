from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import AIMetadata, SubjectId, TopicId, generate_id


@dataclass
class Topic:
    """
    Entity representing a specific topic within a Subject.
    Invariant: A Topic MUST belong to exactly one Subject.
    """

    subject_id: SubjectId
    name: str
    description: str
    id: TopicId = field(default_factory=lambda: TopicId(generate_id()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Topic name cannot be empty.")
        if self.subject_id is None:
            raise ValueError("Topic must belong to a Subject (subject_id cannot be None).")
