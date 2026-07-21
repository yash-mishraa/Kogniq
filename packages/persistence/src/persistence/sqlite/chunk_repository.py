import sqlite3
from datetime import datetime

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics
from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractChunkRepository
from persistence.sqlite.serialization import deserialize, serialize


class SQLiteChunkRepository(AbstractChunkRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    async def save(self, collection: ChunkCollection) -> SaveResult:
        if not collection.chunks:
            return SaveResult(id="", is_new=False)

        document_id = collection.chunks[0].document_id

        # Check if chunks already exist for this document
        row = self._conn.execute(
            "SELECT 1 FROM document_chunks WHERE document_id = ? LIMIT 1", (document_id,)
        ).fetchone()
        is_new = row is None

        # Delete existing chunks for this document (replace strategy)
        self._conn.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))

        for chunk in collection.chunks:
            self._conn.execute(
                """
                INSERT INTO document_chunks (
                    id, document_id, chunk_index, text, title, page_number,
                    section_title, created_at, metadata_json, statistics_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.id,
                    chunk.document_id,
                    chunk.chunk_index,
                    chunk.text,
                    chunk.title,
                    chunk.page_number,
                    chunk.section_title,
                    chunk.created_at.isoformat(),
                    serialize(chunk.metadata),
                    serialize(chunk.statistics),
                ),
            )

        return SaveResult(id=document_id, is_new=is_new)

    async def get_by_document(self, document_id: str) -> ChunkCollection | None:
        rows = self._conn.execute(
            "SELECT * FROM document_chunks WHERE document_id = ? ORDER BY chunk_index",
            (document_id,),
        ).fetchall()

        if not rows:
            return None

        chunks = []
        for row in rows:
            meta_raw = deserialize(row["metadata_json"])
            stats_raw = deserialize(row["statistics_json"])

            # Need to parse processing_timestamp inside statistics manually if it exists
            if "processing_timestamp" in stats_raw and isinstance(
                stats_raw["processing_timestamp"], str
            ):
                stats_raw["processing_timestamp"] = datetime.fromisoformat(
                    stats_raw["processing_timestamp"]
                )

            chunk = Chunk(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                text=row["text"],
                title=row["title"],
                page_number=row["page_number"],
                section_title=row["section_title"],
                created_at=datetime.fromisoformat(row["created_at"]),
                metadata=ChunkMetadata(**meta_raw),
                statistics=ChunkStatistics(**stats_raw),
            )
            chunks.append(chunk)

        return ChunkCollection(chunks=tuple(chunks))

    async def delete(self, document_id: str) -> DeleteResult:
        cursor = self._conn.execute(
            "DELETE FROM document_chunks WHERE document_id = ?", (document_id,)
        )
        return DeleteResult(id=document_id, was_deleted=cursor.rowcount > 0)

    async def statistics(self) -> RepositoryStatistics:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM document_chunks").fetchone()
        return RepositoryStatistics(total_items=row["cnt"])
