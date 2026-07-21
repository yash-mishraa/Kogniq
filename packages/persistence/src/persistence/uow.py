import abc
from typing import Any

from persistence.repositories.base import (
    AbstractChunkRepository,
    AbstractDocumentRepository,
    AbstractKnowledgeRepository,
    AbstractLearningRepository,
)


class AbstractUnitOfWork(abc.ABC):
    """Abstract Unit of Work managing a transaction and providing repositories."""

    documents: AbstractDocumentRepository
    chunks: AbstractChunkRepository
    knowledge: AbstractKnowledgeRepository
    learning: AbstractLearningRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is not None:
                self.rollback()
            else:
                self.commit()
        finally:
            self.close()

    @abc.abstractmethod
    def close(self) -> None:
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        pass

    @abc.abstractmethod
    def rollback(self) -> None:
        pass


class SQLiteUnitOfWork(AbstractUnitOfWork):
    """SQLite implementation of the Unit of Work."""

    def __init__(self, conn_cm: Any, factory: Any) -> None:
        """
        Takes a context manager and a factory capable of producing
        SQLite repositories that share this connection.
        """
        self._conn_cm = conn_cm
        self._conn = self._conn_cm.__enter__()
        self._factory = factory
        # We start a transaction explicitly because connection is in
        # autocommit mode (isolation_level=None)
        self._conn.execute("BEGIN TRANSACTION")

        # Initialize repositories with this shared connection
        self.documents = self._factory.create_document_repository(self._conn)
        self.chunks = self._factory.create_chunk_repository(self._conn)
        self.knowledge = self._factory.create_knowledge_repository(self._conn)
        self.learning = self._factory.create_learning_repository(self._conn)

    def commit(self) -> None:
        self._conn.execute("COMMIT")

    def rollback(self) -> None:
        self._conn.execute("ROLLBACK")

    def close(self) -> None:
        # We suppress exceptions in exit unless we need to handle them.
        self._conn_cm.__exit__(None, None, None)
