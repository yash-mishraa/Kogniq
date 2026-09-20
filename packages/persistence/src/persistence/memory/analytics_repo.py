from collections.abc import Sequence
from typing import Any

from domain.analytics.models import AnalyticsMetrics, LearnerEvent

from persistence.models import SaveResult
from persistence.repositories.base import AbstractAnalyticsRepository


class MemoryAnalyticsRepository(AbstractAnalyticsRepository):
    def __init__(self) -> None:
        self.events: dict[str, LearnerEvent] = {}

    async def list_events_by_resource(self, user_id: str, resource_id: str) -> Sequence[LearnerEvent]:
        # Filter and sort
        filtered = [
            e for e in self.events.values()
            if e.user_id == user_id and e.document_id == resource_id
        ]
        filtered.sort(key=lambda x: x.occurred_at or x.created_at)
        return filtered

    async def has_completed_study(self, user_id: str, document_id: str) -> bool:
        return any(
            e.user_id == user_id
            and e.document_id == document_id
            and e.event_type == "study_session_completed"
            for e in self.events.values()
        )

    async def save_event(self, event: LearnerEvent) -> SaveResult:
        if event.idempotency_key is not None:
            existing = next(
                (e for e in self.events.values() if e.idempotency_key == event.idempotency_key), 
                None
            )
            if existing:
                return SaveResult(id=event.event_id, is_new=False)
                
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

    async def save_events(self, events: Sequence[LearnerEvent]) -> Sequence[SaveResult]:
        from persistence.models import SaveResult
        results = []
        for event in events:
            if event.idempotency_key is not None:
                existing = next(
                    (e for e in self.events.values() if e.idempotency_key == event.idempotency_key), 
                    None
                )
                if existing:
                    results.append(SaveResult(id=event.event_id, is_new=False))
                    continue
                    
            is_new = event.event_id not in self.events
            self.events[event.event_id] = event
            results.append(SaveResult(id=event.event_id, is_new=is_new))
        return results

    async def validate_event_relationships(self, events: Sequence[LearnerEvent]) -> None:
        pass # mock memory repository doesn't check foreign keys natively

    async def get_resource_progress(self, user_id: str, resource_id: str) -> dict[str, Any]:
        user_resource_events = [
            e for e in self.events.values() 
            if e.user_id == user_id and e.document_id == resource_id
        ]
        opened = any(e.event_type == "resource_viewed" for e in user_resource_events)
        viewed_sections = len({e.section_id for e in user_resource_events if e.event_type == "chunk_viewed" and e.section_id})
        viewed_chunks = len({e.chunk_id for e in user_resource_events if e.event_type == "chunk_viewed" and e.chunk_id})
        
        last_activity = max([e.occurred_at or e.created_at for e in user_resource_events]) if user_resource_events else None
        
        return {
            "resource_opened": opened,
            "total_sections": 0, # Cannot compute from events alone, mock 0
            "total_chunks": 0,
            "viewed_sections": viewed_sections,
            "viewed_chunks": viewed_chunks,
            "last_activity": last_activity.isoformat() if last_activity else None
        }
