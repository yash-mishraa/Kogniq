from collections.abc import Sequence

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractChunkRepository


class MemoryChunkRepository(AbstractChunkRepository):
    """In-memory storage for ChunkCollection entities."""

    def __init__(self) -> None:
        self._store: dict[str, ChunkCollection] = {}

    async def save(self, collection: ChunkCollection) -> SaveResult:
        if not collection.chunks:
            raise ValueError("Cannot save empty ChunkCollection")

        document_id = collection.chunks[0].document_id
        is_new = document_id not in self._store
        self._store[document_id] = collection
        return SaveResult(id=document_id, is_new=is_new)

    async def get_by_document(self, document_id: str) -> ChunkCollection | None:
        return self._store.get(document_id)

    async def get_by_ids(self, chunk_ids: Sequence[str]) -> Sequence[Chunk]:
        if not chunk_ids:
            return []

        found_chunks: list[Chunk] = []
        chunk_id_set = set(chunk_ids)

        for collection in self._store.values():
            found_chunks.extend(chunk for chunk in collection.chunks if chunk.id in chunk_id_set)

        return tuple(found_chunks)

    async def delete(self, document_id: str) -> DeleteResult:
        was_deleted = False
        if document_id in self._store:
            del self._store[document_id]
            was_deleted = True
        return DeleteResult(id=document_id, was_deleted=was_deleted)

    async def statistics(self) -> RepositoryStatistics:
        return RepositoryStatistics(total_items=len(self._store))
