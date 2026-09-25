import sqlite3
from typing import Sequence
from datetime import datetime, timezone
from learning_content.notebook import NotebookEntry
from persistence.repositories.notebook import AbstractNotebookRepository

class SQLiteNotebookRepository(AbstractNotebookRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    async def create(self, entry: NotebookEntry) -> None:
        # We rely on SQLite throwing IntegrityError for idempotency_key violations
        self._conn.execute(
            """
            INSERT INTO notebook_entries (
                id, user_id, document_id, title, thoughts_json, created_at, idempotency_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.id,
                entry.user_id,
                entry.document_id,
                entry.title,
                entry.thoughts_json,
                entry.created_at.isoformat(),
                entry.idempotency_key,
            ),
        )

    async def list_by_document(self, document_id: str) -> Sequence[NotebookEntry]:
        cursor = self._conn.execute(
            """
            SELECT id, user_id, document_id, title, thoughts_json, created_at, idempotency_key
            FROM notebook_entries
            WHERE document_id = ?
            ORDER BY created_at ASC
            """,
            (document_id,),
        )
        rows = cursor.fetchall()
        entries = []
        for row in rows:
            entries.append(
                NotebookEntry(
                    id=row[0],
                    user_id=row[1],
                    document_id=row[2],
                    title=row[3],
                    thoughts_json=row[4],
                    created_at=datetime.fromisoformat(row[5]).replace(tzinfo=timezone.utc),
                    idempotency_key=row[6],
                )
            )
        return entries
