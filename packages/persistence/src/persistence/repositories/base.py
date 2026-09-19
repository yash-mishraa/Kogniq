import abc
from collections.abc import Sequence
from typing import Any

from domain.analytics.models import AnalyticsMetrics, LearnerEvent
from knowledge.concept import KnowledgeConcept
from knowledge.relationship import KnowledgeRelationship

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.normalized.document import NormalizedDocument
from learning_content.content import LearningContent
from persistence.models import DeleteResult, DocumentJob, RepositoryStatistics, SaveResult


class AbstractDocumentRepository(abc.ABC):
    """Abstract repository for storing NormalizedDocument entities."""

    @abc.abstractmethod
    async def save(self, document: NormalizedDocument) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get(self, document_id: str) -> NormalizedDocument | None:
        pass

    @abc.abstractmethod
    async def exists(self, document_id: str) -> bool:
        pass

    @abc.abstractmethod
    async def delete(self, document_id: str) -> DeleteResult:
        pass

    @abc.abstractmethod
    async def list(self, user_id: str | None = None) -> Sequence[NormalizedDocument]:
        pass

    @abc.abstractmethod
    async def statistics(self) -> RepositoryStatistics:
        pass


class AbstractChunkRepository(abc.ABC):
    """Abstract repository for storing ChunkCollection entities."""

    @abc.abstractmethod
    async def save(self, collection: ChunkCollection) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get_by_document(self, document_id: str) -> ChunkCollection | None:
        pass

    @abc.abstractmethod
    async def get_by_ids(self, chunk_ids: Sequence[str]) -> Sequence[Chunk]:
        pass

    @abc.abstractmethod
    async def delete(self, document_id: str) -> DeleteResult:
        pass

    @abc.abstractmethod
    async def statistics(self) -> RepositoryStatistics:
        pass


from content.domain.entities import LearningResource, ResourceChunk, ResourceSection


class AbstractLearningResourceRepository(abc.ABC):
    @abc.abstractmethod
    async def save(self, resource: LearningResource) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get(self, resource_id: str, user_id: str) -> LearningResource | None:
        pass

    @abc.abstractmethod
    async def list(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[LearningResource]:
        pass


class AbstractResourceSectionRepository(abc.ABC):
    @abc.abstractmethod
    async def save_all(self, sections: Sequence[ResourceSection]) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get_by_resource(self, resource_id: str, user_id: str) -> Sequence[ResourceSection]:
        pass


class AbstractResourceChunkRepository(abc.ABC):
    @abc.abstractmethod
    async def save_all(self, chunks: Sequence[ResourceChunk]) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get_by_resource(
        self, resource_id: str, user_id: str, limit: int = 100, offset: int = 0
    ) -> Sequence[ResourceChunk]:
        pass

    @abc.abstractmethod
    async def statistics_by_resource(self, resource_id: str, user_id: str) -> dict[str, int]:
        pass


class AbstractConceptRepository(abc.ABC):
    """Abstract repository for storing KnowledgeConcept entities."""

    @abc.abstractmethod
    async def save_all(self, concepts: Sequence[KnowledgeConcept]) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get_by_document(self, document_id: str) -> Sequence[KnowledgeConcept]:
        pass

    @abc.abstractmethod
    async def delete(self, document_id: str) -> DeleteResult:
        pass

    @abc.abstractmethod
    async def statistics(self) -> RepositoryStatistics:
        pass


class AbstractRelationshipRepository(abc.ABC):
    """Abstract repository for storing KnowledgeRelationship entities."""

    @abc.abstractmethod
    async def save_all(self, relationships: Sequence[KnowledgeRelationship]) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get_by_document(self, document_id: str) -> Sequence[KnowledgeRelationship]:
        pass

    @abc.abstractmethod
    async def delete(self, document_id: str) -> DeleteResult:
        pass

    @abc.abstractmethod
    async def statistics(self) -> RepositoryStatistics:
        pass


class AbstractLearningRepository(abc.ABC):
    """Abstract repository for storing generated LearningContent."""

    @abc.abstractmethod
    async def save(self, content: LearningContent) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get(self, content_id: str) -> LearningContent | None:
        pass

    @abc.abstractmethod
    async def list_by_document(self, document_id: str) -> Sequence[LearningContent]:
        pass

    @abc.abstractmethod
    async def delete(self, content_id: str) -> DeleteResult:
        pass

    @abc.abstractmethod
    async def statistics(self) -> RepositoryStatistics:
        pass


class AbstractAnalyticsRepository(abc.ABC):
    """Abstract repository for tracking learning analytics."""

    @abc.abstractmethod
    async def save_event(self, event: LearnerEvent) -> SaveResult:
        pass

    @abc.abstractmethod
    async def save_events(self, events: Sequence[LearnerEvent]) -> Sequence[SaveResult]:
        pass

    @abc.abstractmethod
    async def validate_event_relationships(self, events: Sequence[LearnerEvent]) -> None:
        pass

    @abc.abstractmethod
    async def get_metrics(
        self, user_id: str, days: int | None = None, document_id: str | None = None
    ) -> AnalyticsMetrics:
        pass

    @abc.abstractmethod
    async def has_completed_study(self, user_id: str, document_id: str) -> bool:
        pass

    @abc.abstractmethod
    async def get_resource_progress(self, user_id: str, resource_id: str) -> dict[str, Any]:
        pass


class AbstractDocumentJobRepository(abc.ABC):
    """Abstract repository for tracking document processing jobs."""

    @abc.abstractmethod
    def save(self, job: DocumentJob) -> None:
        pass

    @abc.abstractmethod
    def get(self, job_id: str) -> DocumentJob | None:
        pass

    @abc.abstractmethod
    def list_active(self, user_id: str | None = None) -> Sequence[DocumentJob]:
        pass
