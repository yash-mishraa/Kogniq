from collections.abc import Sequence

from learning_content.content import LearningContent
from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractLearningRepository


class MemoryLearningRepository(AbstractLearningRepository):
    """In-memory storage for LearningContent artifacts."""

    def __init__(self) -> None:
        self._store: dict[str, LearningContent] = {}

    async def save(self, content: LearningContent) -> SaveResult:
        is_new = content.id not in self._store
        self._store[content.id] = content
        return SaveResult(id=content.id, is_new=is_new)

    async def get(self, content_id: str) -> LearningContent | None:
        return self._store.get(content_id)

    async def list_by_document(self, document_id: str) -> Sequence[LearningContent]:
        return [c for c in self._store.values() if c.source_document_id == document_id]

    async def delete(self, content_id: str) -> DeleteResult:
        was_deleted = False
        if content_id in self._store:
            del self._store[content_id]
            was_deleted = True
        return DeleteResult(id=content_id, was_deleted=was_deleted)

    async def statistics(self) -> RepositoryStatistics:
        return RepositoryStatistics(total_items=len(self._store))
