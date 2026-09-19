import sqlite3
from collections.abc import Sequence
from datetime import datetime

from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from content.domain.enums import ProcessingStatus, ResourceType
from persistence.models import SaveResult
from persistence.repositories.base import (
    AbstractLearningResourceRepository,
    AbstractResourceChunkRepository,
    AbstractResourceSectionRepository,
)
from persistence.sqlite.serialization import deserialize


class SQLiteLearningResourceRepository(AbstractLearningResourceRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_resource(self, row: sqlite3.Row) -> LearningResource:
        return LearningResource(
            id=row["id"],
            title=row["title"],
            resource_type=ResourceType(row["resource_type"] or "TEXT"),
            source=row["source"],
            checksum=row["checksum"],
            language=row["language"] or "en",
            status=ProcessingStatus(row["status"] or "UPLOADED"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
            if row["updated_at"]
            else datetime.fromisoformat(row["created_at"]),
        )

    async def save(self, resource: LearningResource) -> SaveResult:
        # Update existing document row since documents are created by ingestion
        self._conn.execute(
            """
            UPDATE documents SET
                resource_type = ?,
                status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                resource.resource_type.value,
                resource.status.value,
                resource.updated_at.isoformat(),
                resource.id,
            ),
        )
        return SaveResult(id=resource.id, is_new=False)

    async def get(self, resource_id: str, user_id: str) -> LearningResource | None:
        row = self._conn.execute(
            "SELECT * FROM documents WHERE id = ? AND user_id = ?",
            (resource_id, user_id),
        ).fetchone()
        if not row:
            return None
        return self._row_to_resource(row)

    async def list(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[LearningResource]:
        rows = self._conn.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset),
        ).fetchall()
        return [self._row_to_resource(r) for r in rows]


class SQLiteResourceSectionRepository(AbstractResourceSectionRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_section(self, row: sqlite3.Row) -> ResourceSection:
        return ResourceSection(
            id=row["id"],
            resource_id=row["document_id"],
            title=row["title"],
            order=row["order_index"],
            page_start=row["page_start"],
            page_end=row["page_end"],
            char_start=row["char_start"],
            char_end=row["char_end"],
        )

    async def save_all(self, sections: Sequence[ResourceSection]) -> SaveResult:
        if not sections:
            return SaveResult(id="", is_new=False)

        resource_id = sections[0].resource_id

        # Replace strategy
        self._conn.execute("DELETE FROM resource_sections WHERE document_id = ?", (resource_id,))

        self._conn.executemany(
            """
            INSERT INTO resource_sections (
                id, document_id, title, order_index, page_start, page_end, char_start, char_end
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    s.id,
                    s.resource_id,
                    s.title,
                    s.order,
                    s.page_start,
                    s.page_end,
                    s.char_start,
                    s.char_end,
                )
                for s in sections
            ],
        )
        return SaveResult(id=resource_id, is_new=True)

    async def get_by_resource(self, resource_id: str, user_id: str) -> Sequence[ResourceSection]:
        # Validate ownership
        doc_row = self._conn.execute(
            "SELECT 1 FROM documents WHERE id = ? AND user_id = ?", (resource_id, user_id)
        ).fetchone()
        if not doc_row:
            return []

        rows = self._conn.execute(
            "SELECT * FROM resource_sections WHERE document_id = ? ORDER BY order_index",
            (resource_id,),
        ).fetchall()
        return [self._row_to_section(r) for r in rows]


class SQLiteResourceChunkRepository(AbstractResourceChunkRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_chunk(self, row: sqlite3.Row) -> ResourceChunk:
        return ResourceChunk(
            id=row["id"],
            resource_id=row["document_id"],
            section_id=row["section_id"],
            text=row["text"],
            order=row["chunk_index"],
            checksum=row["checksum"],
            token_estimate=row["token_estimate"],
            metadata=deserialize(row["metadata_json"]) or {},
        )

    async def save_all(self, chunks: Sequence[ResourceChunk]) -> SaveResult:
        if not chunks:
            return SaveResult(id="", is_new=False)

        resource_id = chunks[0].resource_id

        self._conn.executemany(
            """
            UPDATE document_chunks SET
                section_id = ?,
                checksum = ?,
                token_estimate = ?
            WHERE id = ? AND document_id = ?
            """,
            [
                (
                    c.section_id,
                    c.checksum,
                    c.token_estimate,
                    c.id,
                    c.resource_id,
                )
                for c in chunks
            ],
        )

        return SaveResult(id=resource_id, is_new=False)

    async def get_by_resource(
        self, resource_id: str, user_id: str, limit: int = 100, offset: int = 0
    ) -> Sequence[ResourceChunk]:
        # Validate ownership
        doc_row = self._conn.execute(
            "SELECT 1 FROM documents WHERE id = ? AND user_id = ?", (resource_id, user_id)
        ).fetchone()
        if not doc_row:
            return []

        rows = self._conn.execute(
            """
            SELECT * FROM document_chunks 
            WHERE document_id = ? 
              AND checksum IS NOT NULL
            ORDER BY chunk_index
            LIMIT ? OFFSET ?
            """,
            (resource_id, limit, offset),
        ).fetchall()

        return [self._row_to_chunk(r) for r in rows]

    async def statistics_by_resource(self, resource_id: str, user_id: str) -> dict[str, int]:
        doc_row = self._conn.execute(
            "SELECT 1 FROM documents WHERE id = ? AND user_id = ?", (resource_id, user_id)
        ).fetchone()
        if not doc_row:
            return {"chunk_count": 0, "total_tokens": 0}

        row = self._conn.execute(
            """
            SELECT COUNT(*) as chunk_count, SUM(token_estimate) as total_tokens 
            FROM document_chunks 
            WHERE document_id = ? AND checksum IS NOT NULL
            """,
            (resource_id,)
        ).fetchone()

        return {
            "chunk_count": row["chunk_count"] or 0,
            "total_tokens": row["total_tokens"] or 0,
        }
