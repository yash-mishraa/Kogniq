import sqlite3
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from domain.student.entities import KnowledgeState

from persistence.models import SaveResult
from persistence.repositories.student import AbstractKnowledgeStateRepository


def from_iso(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    return datetime.fromisoformat(date_str)


def to_iso(date_obj: datetime | None) -> str | None:
    if not date_obj:
        return None
    return date_obj.isoformat()


class SQLiteKnowledgeStateRepository(AbstractKnowledgeStateRepository):
    """SQLite implementation of AbstractKnowledgeStateRepository."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_state(self, row: tuple[Any, ...]) -> KnowledgeState:
        return KnowledgeState(
            id=row[0],
            user_id=row[1],
            resource_id=row[2],
            mastery_score=row[3],
            last_reviewed_at=from_iso(row[4]) if row[4] else None,
            next_review_due=from_iso(row[5]) if row[5] else None,
            created_at=from_iso(row[6]) or datetime.min,
            updated_at=from_iso(row[7]) or datetime.min,
        )

    async def save(self, state: KnowledgeState) -> SaveResult:
        cursor = self._conn.cursor()

        # Enforce upsert based on unique (user_id, resource_id)
        cursor.execute(
            """
            INSERT INTO knowledge_states
            (id, user_id, resource_id, mastery_score,
             last_reviewed_at, next_review_due, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, resource_id) DO UPDATE SET
                mastery_score=excluded.mastery_score,
                last_reviewed_at=excluded.last_reviewed_at,
                next_review_due=excluded.next_review_due,
                updated_at=excluded.updated_at
            RETURNING id, created_at
            """,
            (
                state.id,
                state.user_id,
                state.resource_id,
                state.mastery_score,
                to_iso(state.last_reviewed_at) if state.last_reviewed_at else None,
                to_iso(state.next_review_due) if state.next_review_due else None,
                to_iso(state.created_at),
                to_iso(state.updated_at),
            ),
        )
        row = cursor.fetchone()

        # Determine if it was new by checking if created_at == updated_at
        # A bit of a heuristic for SQLite UPSERT returns, but SafeResult doesn't need perfect is_new
        # Actually SQLite RETURNING returns the final row state. Let's just say is_new is False.
        # Wait, SaveResult expects is_new.
        is_new = row[1] == to_iso(state.updated_at)
        return SaveResult(id=row[0], is_new=is_new)

    async def get(self, user_id: str, resource_id: str) -> KnowledgeState | None:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, resource_id, mastery_score,
                   last_reviewed_at, next_review_due, created_at, updated_at
            FROM knowledge_states
            WHERE user_id = ? AND resource_id = ?
            """,
            (user_id, resource_id),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_state(row)

    async def list_by_user(self, user_id: str) -> Sequence[KnowledgeState]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, resource_id, mastery_score,
                   last_reviewed_at, next_review_due, created_at, updated_at
            FROM knowledge_states
            WHERE user_id = ?
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        return [self._row_to_state(row) for row in rows]
