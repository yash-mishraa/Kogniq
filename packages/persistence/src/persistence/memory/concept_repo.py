from collections.abc import Sequence

from knowledge.concept import KnowledgeConcept

from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractConceptRepository


class MemoryConceptRepository(AbstractConceptRepository):
    """In-memory implementation of the concept repository."""

    def __init__(self) -> None:
        # dict mapped by document_id -> concept_id -> KnowledgeConcept
        self._store: dict[str, dict[str, KnowledgeConcept]] = {}

    async def save_all(self, concepts: Sequence[KnowledgeConcept]) -> SaveResult:
        if not concepts:
            return SaveResult(id="batch", is_new=True)

        saved_count = 0
        for concept in concepts:
            doc_id = concept.document_id
            if doc_id not in self._store:
                self._store[doc_id] = {}
            # Upsert logic to handle idempotent updates
            self._store[doc_id][concept.id] = concept
            saved_count += 1

        return SaveResult(id=f"batch_{saved_count}", is_new=True)

    async def get_by_document(self, document_id: str) -> Sequence[KnowledgeConcept]:
        if document_id not in self._store:
            return []
        return list(self._store[document_id].values())

    async def delete(self, document_id: str) -> DeleteResult:
        if document_id in self._store:
            del self._store[document_id]
            return DeleteResult(id=document_id, was_deleted=True)
        return DeleteResult(id=document_id, was_deleted=False)

    async def statistics(self) -> RepositoryStatistics:
        total_concepts = sum(len(doc_concepts) for doc_concepts in self._store.values())
        return RepositoryStatistics(
            total_items=total_concepts,
            storage_size_bytes=total_concepts * 1024,  # Rough estimate
        )
