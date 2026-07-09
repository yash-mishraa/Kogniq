from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import AIMetadata, AssessmentId, QuestionId, generate_id


@dataclass
class Assessment:
    """
    Entity representing a structured evaluation consisting of questions.
    """

    title: str
    id: AssessmentId = field(default_factory=lambda: AssessmentId(generate_id()))
    question_ids: list[QuestionId] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Assessment title cannot be empty.")
