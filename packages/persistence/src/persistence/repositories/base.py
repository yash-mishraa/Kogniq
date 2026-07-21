import abc
from collections.abc import Sequence

from knowledge.graph import KnowledgeGraph

from content.chunking.collection import ChunkCollection
from content.normalized.document import NormalizedDocument
from learning_content.content import LearningContent
from persistence.models import DeleteResult, RepositoryStatistics, SaveResult


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
    async def list(self) -> Sequence[NormalizedDocument]:
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
    async def delete(self, document_id: str) -> DeleteResult:
        pass

    @abc.abstractmethod
    async def statistics(self) -> RepositoryStatistics:
        pass


class AbstractKnowledgeRepository(abc.ABC):
    """Abstract repository for storing KnowledgeGraph entities."""

    @abc.abstractmethod
    async def save(self, document_id: str, graph: KnowledgeGraph) -> SaveResult:
        pass

    @abc.abstractmethod
    async def get(self, document_id: str) -> KnowledgeGraph | None:
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
