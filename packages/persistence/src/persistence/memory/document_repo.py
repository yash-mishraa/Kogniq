from collections.abc import Sequence

from content.normalized.document import NormalizedDocument
from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractDocumentRepository


class MemoryDocumentRepository(AbstractDocumentRepository):
    """In-memory storage for NormalizedDocument entities."""

    def __init__(self) -> None:
        self._store: dict[str, NormalizedDocument] = {}

    async def save(self, document: NormalizedDocument) -> SaveResult:
        is_new = document.id not in self._store
        self._store[document.id] = document
        return SaveResult(id=document.id, is_new=is_new)

    async def get(self, document_id: str) -> NormalizedDocument | None:
        return self._store.get(document_id)

    async def exists(self, document_id: str) -> bool:
        return document_id in self._store

    async def delete(self, document_id: str) -> DeleteResult:
        was_deleted = False
        if document_id in self._store:
            del self._store[document_id]
            was_deleted = True
        return DeleteResult(id=document_id, was_deleted=was_deleted)

    async def list(self) -> Sequence[NormalizedDocument]:
        return list(self._store.values())

    async def statistics(self) -> RepositoryStatistics:
        return RepositoryStatistics(total_items=len(self._store))
