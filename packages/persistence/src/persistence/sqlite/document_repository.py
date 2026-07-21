import sqlite3
from collections.abc import Sequence
from datetime import datetime

from content.normalized.document import NormalizedDocument
from content.normalized.metadata import DocumentMetadata
from content.normalized.page import NormalizedPage
from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractDocumentRepository
from persistence.sqlite.serialization import deserialize, serialize


class SQLiteDocumentRepository(AbstractDocumentRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_document(self, row: sqlite3.Row) -> NormalizedDocument:
        pages_raw = deserialize(row["pages_json"])
        pages = tuple(NormalizedPage(**p) for p in pages_raw)

        metadata_raw = deserialize(row["metadata_json"])
        metadata = DocumentMetadata(**metadata_raw) if metadata_raw else None

        return NormalizedDocument(
            id=row["id"],
            title=row["title"],
            source=row["source"],
            checksum=row["checksum"],
            version=row["version"],
            created_at=datetime.fromisoformat(row["created_at"]),
            language=row["language"],
            metadata=metadata,
            statistics=deserialize(row["statistics_json"]),
            pages=pages,
        )

    async def save(self, document: NormalizedDocument) -> SaveResult:
        row = self._conn.execute("SELECT 1 FROM documents WHERE id = ?", (document.id,)).fetchone()
        is_new = row is None

        metadata_json = serialize(document.metadata) if document.metadata else None
        statistics_json = serialize(document.statistics) if document.statistics else None
        pages_json = serialize(document.pages)

        self._conn.execute(
            """
            INSERT INTO documents (
                id, title, source, checksum, version, created_at, language,
                metadata_json, statistics_json, pages_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                source=excluded.source,
                checksum=excluded.checksum,
                version=excluded.version,
                created_at=excluded.created_at,
                language=excluded.language,
                metadata_json=excluded.metadata_json,
                statistics_json=excluded.statistics_json,
                pages_json=excluded.pages_json
            """,
            (
                document.id,
                document.title,
                document.source,
                document.checksum,
                document.version,
                document.created_at.isoformat(),
                document.language,
                metadata_json,
                statistics_json,
                pages_json,
            ),
        )
        return SaveResult(id=document.id, is_new=is_new)

    async def get(self, document_id: str) -> NormalizedDocument | None:
        row = self._conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        if not row:
            return None
        return self._row_to_document(row)

    async def exists(self, document_id: str) -> bool:
        row = self._conn.execute("SELECT 1 FROM documents WHERE id = ?", (document_id,)).fetchone()
        return row is not None

    async def delete(self, document_id: str) -> DeleteResult:
        cursor = self._conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return DeleteResult(id=document_id, was_deleted=cursor.rowcount > 0)

    async def list(self) -> Sequence[NormalizedDocument]:
        rows = self._conn.execute("SELECT * FROM documents").fetchall()
        return [self._row_to_document(row) for row in rows]

    async def statistics(self) -> RepositoryStatistics:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM documents").fetchone()
        return RepositoryStatistics(total_items=row["cnt"])
