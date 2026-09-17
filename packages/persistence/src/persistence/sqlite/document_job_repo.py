import sqlite3
from collections.abc import Sequence
from datetime import datetime

from persistence.models import DocumentJob
from persistence.repositories.base import AbstractDocumentJobRepository


class SQLiteDocumentJobRepository(AbstractDocumentJobRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, job: DocumentJob) -> None:
        self._conn.execute(
            """
            INSERT INTO document_jobs (id, user_id, filename, status, created_at, error_message) 
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET 
                status=excluded.status, 
                error_message=excluded.error_message
            """,
            (
                job.id,
                job.user_id,
                job.filename,
                job.status,
                job.created_at.isoformat(),
                job.error_message,
            ),
        )

    def get(self, job_id: str) -> DocumentJob | None:
        row = self._conn.execute(
            "SELECT id, user_id, filename, status, created_at, error_message FROM document_jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
        if not row:
            return None
        return DocumentJob(
            id=row["id"],
            user_id=row["user_id"],
            filename=row["filename"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            error_message=row["error_message"],
        )

    def list_active(self, user_id: str | None = None) -> Sequence[DocumentJob]:
        query = "SELECT id, user_id, filename, status, created_at, error_message FROM document_jobs WHERE status != 'Ready'"
        params = []
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        rows = self._conn.execute(query, params).fetchall()
        return [
            DocumentJob(
                id=r["id"],
                user_id=r["user_id"],
                filename=r["filename"],
                status=r["status"],
                created_at=datetime.fromisoformat(r["created_at"]),
                error_message=r["error_message"],
            )
            for r in rows
        ]
