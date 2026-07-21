import abc
import sqlite3
from typing import Any

from persistence.memory import (
    MemoryChunkRepository,
    MemoryDocumentRepository,
    MemoryKnowledgeRepository,
    MemoryLearningRepository,
)
from persistence.repositories.base import (
    AbstractChunkRepository,
    AbstractDocumentRepository,
    AbstractKnowledgeRepository,
    AbstractLearningRepository,
)
from persistence.sqlite.chunk_repository import SQLiteChunkRepository
from persistence.sqlite.document_repository import SQLiteDocumentRepository
from persistence.sqlite.knowledge_repository import SQLiteKnowledgeRepository
from persistence.sqlite.learning_repository import SQLiteLearningRepository


class AbstractRepositoryFactory(abc.ABC):
    """Abstract factory for creating concrete repository implementations."""

    @abc.abstractmethod
    def create_document_repository(self, conn: Any = None) -> AbstractDocumentRepository:
        pass

    @abc.abstractmethod
    def create_chunk_repository(self, conn: Any = None) -> AbstractChunkRepository:
        pass

    @abc.abstractmethod
    def create_knowledge_repository(self, conn: Any = None) -> AbstractKnowledgeRepository:
        pass

    @abc.abstractmethod
    def create_learning_repository(self, conn: Any = None) -> AbstractLearningRepository:
        pass


class MemoryRepositoryFactory(AbstractRepositoryFactory):
    """Provides singleton in-memory repositories."""

    def __init__(self) -> None:
        self._document_repo = MemoryDocumentRepository()
        self._chunk_repo = MemoryChunkRepository()
        self._knowledge_repo = MemoryKnowledgeRepository()
        self._learning_repo = MemoryLearningRepository()

    def create_document_repository(self, conn: Any = None) -> AbstractDocumentRepository:  # noqa: ARG002
        return self._document_repo

    def create_chunk_repository(self, conn: Any = None) -> AbstractChunkRepository:  # noqa: ARG002
        return self._chunk_repo

    def create_knowledge_repository(self, conn: Any = None) -> AbstractKnowledgeRepository:  # noqa: ARG002
        return self._knowledge_repo

    def create_learning_repository(self, conn: Any = None) -> AbstractLearningRepository:  # noqa: ARG002
        return self._learning_repo


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

    def create_knowledge_repository(
        self, conn: sqlite3.Connection | None = None
    ) -> AbstractKnowledgeRepository:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteKnowledgeRepository(conn)

    def create_learning_repository(
        self, conn: sqlite3.Connection | None = None
    ) -> AbstractLearningRepository:
        if not conn:
            raise ValueError("SQLite repositories require a connection instance.")
        return SQLiteLearningRepository(conn)
