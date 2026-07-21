from persistence.factory import MemoryRepositoryFactory
from persistence.uow import AbstractUnitOfWork


class MemoryUnitOfWork(AbstractUnitOfWork):
    """In-memory Unit of Work."""

    def __init__(self, factory: MemoryRepositoryFactory) -> None:
        self.documents = factory.create_document_repository()
        self.chunks = factory.create_chunk_repository()
        self.knowledge = factory.create_knowledge_repository()
        self.learning = factory.create_learning_repository()

    def commit(self) -> None:
        # In-memory repositories just save instantly, so commit is a no-op.
        pass

    def rollback(self) -> None:
        # Rollback not supported for in-memory in this prototype.
        pass

    def close(self) -> None:
        pass
