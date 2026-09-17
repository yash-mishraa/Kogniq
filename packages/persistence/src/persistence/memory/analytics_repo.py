from domain.analytics.models import AnalyticsMetrics, LearnerEvent

from persistence.models import SaveResult
from persistence.repositories.base import AbstractAnalyticsRepository


class MemoryAnalyticsRepository(AbstractAnalyticsRepository):
    def __init__(self) -> None:
        self.events: dict[str, LearnerEvent] = {}

    async def has_completed_study(self, user_id: str, document_id: str) -> bool:
        return any(
            e.user_id == user_id
            and e.document_id == document_id
            and e.event_type == "study_session_completed"
            for e in self.events.values()
        )

    async def save_event(self, event: LearnerEvent) -> SaveResult:
        is_new = event.event_id not in self.events
        self.events[event.event_id] = event
        return SaveResult(id=event.event_id, is_new=is_new)

    async def get_metrics(
        self, user_id: str, days: int | None = None, document_id: str | None = None
    ) -> AnalyticsMetrics:
        from datetime import UTC, datetime, timedelta

        user_events = [e for e in self.events.values() if e.user_id == user_id]
        if days is not None:
            cutoff = datetime.now(UTC) - timedelta(days=days)
            user_events = [e for e in user_events if e.created_at >= cutoff]

        if document_id is not None:
            user_events = [e for e in user_events if e.document_id == document_id]

        fc = len([e for e in user_events if e.event_type == "flashcard_reviewed"])
        qz = [e for e in user_events if e.event_type == "quiz_completed"]

        qc = len(qz)
        ts = sum(e.event_data.get("score", 0) for e in qz)
        tq = sum(e.event_data.get("total_questions", 0) for e in qz)

        acc = ts / tq if tq > 0 else 0.0

        return AnalyticsMetrics(
            quizzes_completed=qc, average_quiz_accuracy=acc, flashcards_reviewed=fc
        )
