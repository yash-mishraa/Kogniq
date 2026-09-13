import json
import sqlite3
from datetime import UTC, datetime, timedelta

from domain.analytics.models import AnalyticsMetrics, LearnerEvent

from persistence.models import SaveResult
from persistence.repositories.base import AbstractAnalyticsRepository


class SQLiteAnalyticsRepository(AbstractAnalyticsRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    async def save_event(self, event: LearnerEvent) -> SaveResult:
        row = self._conn.execute("SELECT 1 FROM learner_activity WHERE id = ?", (event.event_id,)).fetchone()
        is_new = row is None

        self._conn.execute(
            """
            INSERT INTO learner_activity (
                id, user_id, document_id, event_type, event_data_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                event_data_json=excluded.event_data_json,
                created_at=excluded.created_at
            """,
            (
                event.event_id,
                event.user_id,
                event.document_id,
                event.event_type,
                json.dumps(event.event_data),
                event.created_at.isoformat(),
            )
        )
        return SaveResult(id=event.event_id, is_new=is_new)

    async def get_metrics(self, user_id: str, days: int | None = None) -> AnalyticsMetrics:
        query_conditions = ["user_id = ?"]
        params = [user_id]
        
        if days is not None:
            cutoff = datetime.now(UTC) - timedelta(days=days)
            query_conditions.append("created_at >= ?")
            params.append(cutoff.isoformat())
            
        where_clause = " AND ".join(query_conditions)
        
        # Flashcards
        fc_row = self._conn.execute(
            f"SELECT COUNT(*) as cnt FROM learner_activity WHERE event_type = 'flashcard_reviewed' AND {where_clause}",
            params
        ).fetchone()
        flashcards_reviewed = fc_row["cnt"] if fc_row else 0
        
        # Quizzes
        quiz_rows = self._conn.execute(
            f"SELECT event_data_json FROM learner_activity WHERE event_type = 'quiz_completed' AND {where_clause}",
            params
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
            flashcards_reviewed=flashcards_reviewed
        )
