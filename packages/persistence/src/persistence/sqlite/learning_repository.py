import sqlite3
from collections.abc import Sequence
from datetime import datetime

from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics
from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractLearningRepository
from persistence.sqlite.serialization import deserialize, serialize


class SQLiteLearningRepository(AbstractLearningRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_content(self, row: sqlite3.Row) -> LearningContent:
        meta_raw = deserialize(row["metadata_json"])
        stats_raw = deserialize(row["statistics_json"])
        source_chunks = tuple(deserialize(row["source_chunk_ids_json"]))

        return LearningContent(
            id=row["id"],
            source_document_id=row["source_document_id"],
            source_chunk_ids=source_chunks,
            content_type=ContentType[row["content_type"]],
            title=row["title"],
            body=row["body"],
            created_at=datetime.fromisoformat(row["created_at"]),
            metadata=LearningContentMetadata(**meta_raw),
            statistics=LearningContentStatistics(**stats_raw),
        )

    async def save(self, content: LearningContent) -> SaveResult:
        row = self._conn.execute(
            "SELECT 1 FROM learning_content WHERE id = ?", (content.id,)
        ).fetchone()
        is_new = row is None

        self._conn.execute(
            """
            INSERT INTO learning_content (
                id, source_document_id, content_type, title, body, created_at,
                source_chunk_ids_json, metadata_json, statistics_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                body=excluded.body,
                metadata_json=excluded.metadata_json,
                statistics_json=excluded.statistics_json
            """,
            (
                content.id,
                content.source_document_id,
                content.content_type.name,
                content.title,
                content.body,
                content.created_at.isoformat(),
                serialize(content.source_chunk_ids),
                serialize(content.metadata),
                serialize(content.statistics),
            ),
        )
        return SaveResult(id=content.id, is_new=is_new)

    async def get(self, content_id: str) -> LearningContent | None:
        row = self._conn.execute(
            "SELECT * FROM learning_content WHERE id = ?", (content_id,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_content(row)

    async def list_by_document(self, document_id: str) -> Sequence[LearningContent]:
        rows = self._conn.execute(
            "SELECT * FROM learning_content WHERE source_document_id = ? ORDER BY created_at DESC",
            (document_id,),
        ).fetchall()
        return [self._row_to_content(row) for row in rows]

    async def delete(self, content_id: str) -> DeleteResult:
        cursor = self._conn.execute("DELETE FROM learning_content WHERE id = ?", (content_id,))
        return DeleteResult(id=content_id, was_deleted=cursor.rowcount > 0)

    async def statistics(self) -> RepositoryStatistics:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM learning_content").fetchone()
        return RepositoryStatistics(total_items=row["cnt"])
