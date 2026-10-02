import sqlite3
from collections.abc import Sequence
from datetime import datetime, timezone
import json

from content.normalized.semantics import DocumentSemantics
from persistence.models import SaveResult
from persistence.repositories.base import AbstractSemanticRepository


class SQLiteSemanticRepository(AbstractSemanticRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_model(self, row: sqlite3.Row) -> DocumentSemantics:
        return DocumentSemantics(
            id=row["id"],
            document_id=row["document_id"],
            semantic_version=row["semantic_version"],
            status=row["status"],
            is_active=bool(row["is_active"]),
            semantics_json=row["semantics_json"],
            created_at=datetime.fromisoformat(row["created_at"]),
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
        )

    async def save(self, semantics: DocumentSemantics) -> SaveResult:
        try:
            completed_at_str = semantics.completed_at.isoformat() if semantics.completed_at else None
            self._conn.execute(
                """
                INSERT INTO document_semantics (
                    id, document_id, semantic_version, status, is_active, semantics_json, created_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status,
                    is_active=excluded.is_active,
                    semantics_json=excluded.semantics_json,
                    completed_at=excluded.completed_at
                """,
                (
                    semantics.id,
                    semantics.document_id,
                    semantics.semantic_version,
                    semantics.status,
                    1 if semantics.is_active else 0,
                    semantics.semantics_json,
                    semantics.created_at.isoformat(),
                    completed_at_str,
                )
            )
            return SaveResult(id=semantics.id, is_new=True)
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {e}")

    async def get_active(self, document_id: str) -> DocumentSemantics | None:
        cursor = self._conn.execute(
            "SELECT * FROM document_semantics WHERE document_id = ? AND is_active = 1",
            (document_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    async def list_by_document(self, document_id: str) -> Sequence[DocumentSemantics]:
        cursor = self._conn.execute(
            "SELECT * FROM document_semantics WHERE document_id = ? ORDER BY created_at DESC",
            (document_id,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]

    async def activate_version(self, document_id: str, semantic_id: str) -> bool:
        # Atomic activation rule:
        # We activate if the new semantic_id belongs to a version >= the currently active version.
        try:
            # 1. find the semantic_version of the target semantic_id
            cursor = self._conn.execute(
                "SELECT semantic_version FROM document_semantics WHERE id = ?",
                (semantic_id,)
            )
            target_row = cursor.fetchone()
            if not target_row:
                return False
            
            target_version = target_row["semantic_version"]
            
            # 2. find current active version
            cursor = self._conn.execute(
                "SELECT semantic_version FROM document_semantics WHERE document_id = ? AND is_active = 1",
                (document_id,)
            )
            row = cursor.fetchone()
            current_active_v = row["semantic_version"] if row else "0"

            # Parse to int as required by P1-D1 architecture
            try:
                curr_v = int(current_active_v)
            except ValueError:
                curr_v = 0
            
            try:
                new_v = int(target_version)
            except ValueError:
                new_v = 0
            
            # 3. Intentional behavior: We allow overwriting the same version.
            # If two jobs finish version 1, the later one to call activate_version wins,
            # and uniquely sets its row to active, deactivating the other.
            if new_v >= curr_v:
                # Deactivate all
                self._conn.execute(
                    "UPDATE document_semantics SET is_active = 0 WHERE document_id = ?",
                    (document_id,)
                )
                # Activate uniquely by ID
                self._conn.execute(
                    "UPDATE document_semantics SET is_active = 1 WHERE id = ?",
                    (semantic_id,)
                )
                return True
            return False
        except sqlite3.Error:
            return False
