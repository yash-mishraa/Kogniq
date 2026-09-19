from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class LearnerEvent:
    event_id: str
    user_id: str
    document_id: str  # alias for resource_id
    event_type: str
    event_data: dict[str, Any]
    created_at: datetime
    section_id: str | None = None
    chunk_id: str | None = None
    occurred_at: datetime | None = None
    idempotency_key: str | None = None

    @property
    def resource_id(self) -> str:
        return self.document_id


@dataclass(frozen=True)
class QuizCompletedEvent(LearnerEvent):
    @property
    def score(self) -> int:
        return int(self.event_data.get("score", 0))

    @property
    def total_questions(self) -> int:
        return int(self.event_data.get("total_questions", 0))


@dataclass(frozen=True)
class StudySessionCompletedEvent(LearnerEvent):
    @property
    def completed_at(self) -> str:
        return str(self.event_data.get("completed_at", ""))


@dataclass(frozen=True)
class FlashcardReviewedEvent(LearnerEvent):
    @property
    def card_id(self) -> str:
        return str(self.event_data.get("card_id", ""))

    @property
    def difficulty(self) -> str:
        return str(self.event_data.get("difficulty", ""))


@dataclass(frozen=True)
class AnalyticsMetrics:
    quizzes_completed: int
    average_quiz_accuracy: float
    flashcards_reviewed: int

@dataclass(frozen=True)
class ResourceViewedEvent(LearnerEvent):
    pass

@dataclass(frozen=True)
class ChunkViewedEvent(LearnerEvent):
    pass
