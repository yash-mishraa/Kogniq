from knowledge.graph import KnowledgeGraph

from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractKnowledgeRepository


class MemoryKnowledgeRepository(AbstractKnowledgeRepository):
    """In-memory storage for KnowledgeGraph entities."""

    def __init__(self) -> None:
        self._store: dict[str, KnowledgeGraph] = {}

    async def save(self, document_id: str, graph: KnowledgeGraph) -> SaveResult:
        if not document_id:
            raise ValueError("Cannot save KnowledgeGraph without document_id")

        is_new = document_id not in self._store
        self._store[document_id] = graph
        return SaveResult(id=document_id, is_new=is_new)

    async def get(self, document_id: str) -> KnowledgeGraph | None:
        return self._store.get(document_id)

    async def delete(self, document_id: str) -> DeleteResult:
        was_deleted = False
        if document_id in self._store:
            del self._store[document_id]
            was_deleted = True
        return DeleteResult(id=document_id, was_deleted=was_deleted)

    async def statistics(self) -> RepositoryStatistics:
        return RepositoryStatistics(total_items=len(self._store))
