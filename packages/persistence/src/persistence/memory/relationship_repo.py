from collections.abc import Sequence

from knowledge.relationship import KnowledgeRelationship

from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractRelationshipRepository


class MemoryRelationshipRepository(AbstractRelationshipRepository):
    """In-memory implementation of the relationship repository."""

    def __init__(self) -> None:
        # dict mapped by document_id -> relationship_id -> KnowledgeRelationship
        self._store: dict[str, dict[str, KnowledgeRelationship]] = {}

    async def save_all(self, relationships: Sequence[KnowledgeRelationship]) -> SaveResult:
        if not relationships:
            return SaveResult(id="batch", is_new=True)

        saved_count = 0
        for relationship in relationships:
            doc_id = relationship.document_id
            if doc_id not in self._store:
                self._store[doc_id] = {}
            # Upsert logic to handle idempotent updates
            self._store[doc_id][relationship.id] = relationship
            saved_count += 1

        return SaveResult(id=f"batch_{saved_count}", is_new=True)

    async def get_by_document(self, document_id: str) -> Sequence[KnowledgeRelationship]:
        if document_id not in self._store:
            return []
        return list(self._store[document_id].values())

    async def delete(self, document_id: str) -> DeleteResult:
        if document_id in self._store:
            del self._store[document_id]
            return DeleteResult(id=document_id, was_deleted=True)
        return DeleteResult(id=document_id, was_deleted=False)

    async def statistics(self) -> RepositoryStatistics:
        total_relationships = sum(len(doc_rels) for doc_rels in self._store.values())
        return RepositoryStatistics(
            total_items=total_relationships,
            storage_size_bytes=total_relationships * 1024,  # Rough estimate
        )
