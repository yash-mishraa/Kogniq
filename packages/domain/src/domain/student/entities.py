from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class KnowledgeState:
    """
    Represents a learner's synthesized mastery and review schedule 
    for a specific learning resource.
    """
    id: str
    user_id: str
    resource_id: str
    mastery_score: float  # constrained 0.0 - 1.0
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: datetime | None = None
    next_review_due: datetime | None = None

    def __post_init__(self) -> None:
        if not (0.0 <= self.mastery_score <= 1.0):
            raise ValueError(f"mastery_score must be between 0.0 and 1.0, got {self.mastery_score}")
