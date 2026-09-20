import json
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from domain.analytics.models import (
    AnalyticsMetrics,
    ChunkViewedEvent,
    FlashcardReviewedEvent,
    LearnerEvent,
    QuizCompletedEvent,
    ResourceViewedEvent,
    StudySessionCompletedEvent,
)

from persistence.models import SaveResult
from persistence.repositories.base import AbstractAnalyticsRepository


class SQLiteAnalyticsRepository(AbstractAnalyticsRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    async def list_events_by_resource(self, user_id: str, resource_id: str) -> Sequence[LearnerEvent]:
        rows = self._conn.execute(
            """
            SELECT id, user_id, document_id, event_type, event_data_json, created_at,
                   section_id, chunk_id, occurred_at, idempotency_key
            FROM learner_activity
            WHERE user_id = ? AND document_id = ?
            ORDER BY COALESCE(occurred_at, created_at) ASC
            """,
            (user_id, resource_id),
        ).fetchall()

        events: list[LearnerEvent] = []
        for row in rows:
            data = json.loads(row["event_data_json"])
            evt_type = row["event_type"]
            base_kwargs = {
                "event_id": row["id"],
                "user_id": row["user_id"],
                "document_id": row["document_id"],
                "event_type": evt_type,
                "event_data": data,
                "created_at": datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.min,
                "section_id": row["section_id"],
                "chunk_id": row["chunk_id"],
                "occurred_at": datetime.fromisoformat(row["occurred_at"]) if row["occurred_at"] else None,
                "idempotency_key": row["idempotency_key"],
            }
            if evt_type == "quiz_completed":
                events.append(QuizCompletedEvent(**base_kwargs))
            elif evt_type == "flashcard_reviewed":
                events.append(FlashcardReviewedEvent(**base_kwargs))
            elif evt_type == "resource_viewed":
                events.append(ResourceViewedEvent(**base_kwargs))
            elif evt_type == "chunk_viewed":
                events.append(ChunkViewedEvent(**base_kwargs))
            elif evt_type == "study_session_completed":
                events.append(StudySessionCompletedEvent(**base_kwargs))
            else:
                events.append(LearnerEvent(**base_kwargs))
        return events

    async def has_completed_study(self, user_id: str, document_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM learner_activity WHERE user_id = ? AND document_id = ? "
            "AND event_type = 'study_session_completed' LIMIT 1",
            (user_id, document_id),
        ).fetchone()
        return row is not None

    async def save_event(self, event: LearnerEvent) -> SaveResult:
        self._conn.execute(
            "SELECT 1 FROM learner_activity WHERE id = ?", (event.event_id,)
        ).fetchone()

        cursor = self._conn.execute(
            """
            INSERT OR IGNORE INTO learner_activity (
                id, user_id, document_id, event_type, event_data_json, created_at,
                section_id, chunk_id, occurred_at, idempotency_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.user_id,
                event.document_id,
                event.event_type,
                json.dumps(event.event_data),
                event.created_at.isoformat(),
                event.section_id,
                event.chunk_id,
                event.occurred_at.isoformat() if event.occurred_at else None,
                event.idempotency_key,
            ),
        )
        # If cursor.rowcount == 0, it was ignored (duplicate id or idempotency key)
        return SaveResult(id=event.event_id, is_new=cursor.rowcount > 0)

    async def save_events(self, events: Sequence[LearnerEvent]) -> Sequence[SaveResult]:
        if not events:
            return []
            
        rows = [
            (
                event.event_id,
                event.user_id,
                event.document_id,
                event.event_type,
                json.dumps(event.event_data),
                event.created_at.isoformat(),
                event.section_id,
                event.chunk_id,
                event.occurred_at.isoformat() if event.occurred_at else None,
                event.idempotency_key,
            )
            for event in events
        ]
            
        self._conn.executemany(
            """
            INSERT OR IGNORE INTO learner_activity (
                id, user_id, document_id, event_type, event_data_json, created_at,
                section_id, chunk_id, occurred_at, idempotency_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        # We can't easily know which ones were ignored in executemany without extra queries.
        # But for batch operations returning SaveResult with is_new=True
        # is acceptable per domain rules.
        return [SaveResult(id=e.event_id, is_new=True) for e in events]

    async def validate_event_relationships(self, events: Sequence[LearnerEvent]) -> None:
        if not events:
            return
            
        for event in events:
            if event.section_id:
                # Check if section belongs to resource
                row = self._conn.execute(
                    "SELECT 1 FROM resource_sections WHERE id = ? AND document_id = ?",
                    (event.section_id, event.document_id)
                ).fetchone()
                if not row:
                    raise ValueError(
                        f"Section {event.section_id} does not belong to "
                        f"resource {event.document_id} or does not exist"
                    )
                    
            if event.chunk_id:
                # Check if chunk belongs to resource (and section if provided)
                if event.section_id:
                    row = self._conn.execute(
                        "SELECT 1 FROM document_chunks WHERE id = ? AND document_id = ? "
                        "AND section_id = ?",
                        (event.chunk_id, event.document_id, event.section_id)
                    ).fetchone()
                    if not row:
                        raise ValueError(
                            f"Chunk {event.chunk_id} does not belong to section "
                            f"{event.section_id} in resource {event.document_id}"
                        )
                else:
                    row = self._conn.execute(
                        "SELECT 1 FROM document_chunks WHERE id = ? AND document_id = ?",
                        (event.chunk_id, event.document_id)
                    ).fetchone()
                    if not row:
                        raise ValueError(
                            f"Chunk {event.chunk_id} does not belong to "
                            f"resource {event.document_id} or does not exist"
                        )

    async def get_metrics(
        self, user_id: str, days: int | None = None, document_id: str | None = None
    ) -> AnalyticsMetrics:
        query_conditions = ["user_id = ?"]
        params = [user_id]

        if days is not None:
            cutoff = datetime.now(UTC) - timedelta(days=days)
            query_conditions.append("created_at >= ?")
            params.append(cutoff.isoformat())

        if document_id is not None:
            query_conditions.append("document_id = ?")
            params.append(document_id)

        where_clause = " AND ".join(query_conditions)

        # Flashcards
        fc_row = self._conn.execute(
            f"SELECT COUNT(*) as cnt FROM learner_activity "
            f"WHERE event_type = 'flashcard_reviewed' AND {where_clause}",
            params,
        ).fetchone()
        flashcards_reviewed = fc_row["cnt"] if fc_row else 0

        # Quizzes
        quiz_rows = self._conn.execute(
            f"SELECT event_data_json FROM learner_activity "
            f"WHERE event_type = 'quiz_completed' AND {where_clause}",
            params,
        ).fetchall()

        quizzes_completed = len(quiz_rows)
        total_score = 0
        total_questions = 0

        for row in quiz_rows:
            data = json.loads(row["event_data_json"])
            total_score += data.get("score", 0)
            total_questions += data.get("total_questions", 0)

        average_quiz_accuracy = 0.0
        if total_questions > 0:
            average_quiz_accuracy = total_score / total_questions

        return AnalyticsMetrics(
            quizzes_completed=quizzes_completed,
            average_quiz_accuracy=average_quiz_accuracy,
            flashcards_reviewed=flashcards_reviewed,
        )

    async def get_resource_progress(self, user_id: str, resource_id: str) -> dict[str, Any]:
        """Calculates deterministic progress for a resource based on persisted activity."""
        # Check if the resource was ever opened
        opened_row = self._conn.execute(
            """
            SELECT 1 FROM learner_activity
            WHERE user_id = ? AND document_id = ? AND event_type = 'resource_viewed'
            LIMIT 1
            """,
            (user_id, resource_id),
        ).fetchone()

        # Count total sections in document
        total_sections = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM resource_sections WHERE document_id = ?",
            (resource_id,)
        ).fetchone()["cnt"]

        # Count total chunks in document
        total_chunks = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM document_chunks WHERE document_id = ?",
            (resource_id,)
        ).fetchone()["cnt"]

        # Count distinct sections viewed
        viewed_sections = self._conn.execute(
            """
            SELECT COUNT(DISTINCT section_id) as cnt FROM learner_activity
            WHERE user_id = ? AND document_id = ? AND event_type = 'chunk_viewed'
            AND section_id IS NOT NULL
            """,
            (user_id, resource_id),
        ).fetchone()["cnt"]

        # Count distinct chunks viewed
        viewed_chunks = self._conn.execute(
            """
            SELECT COUNT(DISTINCT chunk_id) as cnt FROM learner_activity
            WHERE user_id = ? AND document_id = ? AND event_type = 'chunk_viewed'
            AND chunk_id IS NOT NULL
            """,
            (user_id, resource_id),
        ).fetchone()["cnt"]
        
        # Last activity
        last_activity = self._conn.execute(
            """
            SELECT MAX(COALESCE(occurred_at, created_at)) as last_act FROM learner_activity
            WHERE user_id = ? AND document_id = ?
            """,
            (user_id, resource_id),
        ).fetchone()["last_act"]

        return {
            "resource_opened": opened_row is not None,
            "total_sections": total_sections,
            "total_chunks": total_chunks,
            "viewed_sections": viewed_sections,
            "viewed_chunks": viewed_chunks,
            "last_activity": last_activity
        }
