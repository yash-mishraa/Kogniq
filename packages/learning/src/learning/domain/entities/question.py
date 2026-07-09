from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..exceptions import InvalidQuestionEvaluationError
from ..value_objects import (
    AIMetadata,
    Difficulty,
    LearningObjectiveId,
    QuestionId,
    Tag,
    generate_id,
)


@dataclass
class Question:
    """
    Entity representing a testable item.
    Invariant: Must evaluate at least one LearningObjective.
    """

    prompt_text: str
    learning_objective_ids: set[LearningObjectiveId]
    id: QuestionId = field(default_factory=lambda: QuestionId(generate_id()))
    difficulty: Difficulty | None = None
    tags: set[Tag] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.prompt_text or not self.prompt_text.strip():
            raise ValueError("Question prompt cannot be empty.")
        if not self.learning_objective_ids:
            raise InvalidQuestionEvaluationError(
                "A Question must evaluate at least one LearningObjective."
            )
