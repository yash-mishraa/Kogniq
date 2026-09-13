import abc
import sqlite3
from typing import Any

from persistence.memory import (
    MemoryChunkRepository,
    MemoryConceptRepository,
    MemoryDocumentRepository,
    MemoryLearningRepository,
    MemoryRelationshipRepository,
)
from persistence.repositories.base import (
    AbstractChunkRepository,
    AbstractConceptRepository,
    AbstractDocumentRepository,
    AbstractLearningRepository,
    AbstractRelationshipRepository,
)
from persistence.sqlite.analytics_repository import SQLiteAnalyticsRepository
from persistence.sqlite.chunk_repository import SQLiteChunkRepository
from persistence.sqlite.concept_repository import SQLiteConceptRepository
from persistence.sqlite.document_repository import SQLiteDocumentRepository
from persistence.sqlite.learning_repository import SQLiteLearningRepository
from persistence.sqlite.relationship_repository import SQLiteRelationshipRepository


class AbstractRepositoryFactory(abc.ABC):
    """Abstract factory for creating concrete repository implementations."""

    @abc.abstractmethod
    def create_document_repository(self, conn: Any = None) -> AbstractDocumentRepository:
        pass

    @abc.abstractmethod
    def create_chunk_repository(self, conn: Any = None) -> AbstractChunkRepository:
        pass

    @abc.abstractmethod
    def create_concept_repository(self, conn: Any = None) -> AbstractConceptRepository:
        pass

    @abc.abstractmethod
    def create_relationship_repository(self, conn: Any = None) -> AbstractRelationshipRepository:
        pass

    @abc.abstractmethod
    def create_learning_repository(self, conn: Any = None) -> AbstractLearningRepository:
        pass

    @abc.abstractmethod
    def create_analytics_repository(self, conn: Any = None) -> Any:
        pass


class MemoryRepositoryFactory(AbstractRepositoryFactory):
    """Provides singleton in-memory repositories."""

    def __init__(self) -> None:
        self._document_repo = MemoryDocumentRepository()
        self._chunk_repo = MemoryChunkRepository()
        self._concept_repo = MemoryConceptRepository()
        self._relationship_repo = MemoryRelationshipRepository()
        self._learning_repo = MemoryLearningRepository()
        from persistence.memory.analytics_repo import MemoryAnalyticsRepository

        self._analytics_repo = MemoryAnalyticsRepository()

    def create_document_repository(self, conn: Any = None) -> AbstractDocumentRepository:  # noqa: ARG002
        return self._document_repo

    def create_chunk_repository(self, conn: Any = None) -> AbstractChunkRepository:  # noqa: ARG002
        return self._chunk_repo

    def create_concept_repository(self, conn: Any = None) -> AbstractConceptRepository:  # noqa: ARG002
        return self._concept_repo

    def create_relationship_repository(self, conn: Any = None) -> AbstractRelationshipRepository:  # noqa: ARG002
        return self._relationship_repo

    def create_learning_repository(self, conn: Any = None) -> AbstractLearningRepository:  # noqa: ARG002
        return self._learning_repo

    def create_analytics_repository(self, conn: Any = None) -> Any:  # noqa: ARG002
        return self._analytics_repo


class SQLiteRepositoryFactory(AbstractRepositoryFactory):
    """Provides SQLite repositories."""

    def create_document_repository(
        self, conn: sqlite3.Connection | None = None
    ) -> AbstractDocumentRepository:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteDocumentRepository(conn)

    def create_chunk_repository(
        self, conn: sqlite3.Connection | None = None
    ) -> AbstractChunkRepository:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteChunkRepository(conn)

    def create_concept_repository(
        self, conn: sqlite3.Connection | None = None
    ) -> AbstractConceptRepository:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteConceptRepository(conn)

    def create_relationship_repository(
        self, conn: sqlite3.Connection | None = None
    ) -> AbstractRelationshipRepository:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteRelationshipRepository(conn)

    def create_learning_repository(
        self, conn: sqlite3.Connection | None = None
    ) -> AbstractLearningRepository:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteLearningRepository(conn)

    def create_analytics_repository(self, conn: sqlite3.Connection | None = None) -> Any:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteAnalyticsRepository(conn)
