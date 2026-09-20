from persistence.factory import MemoryRepositoryFactory
from persistence.uow import AbstractUnitOfWork


class MemoryUnitOfWork(AbstractUnitOfWork):
    """In-memory Unit of Work."""

    def __init__(self, factory: MemoryRepositoryFactory) -> None:
        self.documents = factory.create_document_repository()
        self.chunks = factory.create_chunk_repository()
        self.concepts = factory.create_concept_repository()
        self.relationships = factory.create_relationship_repository()
        self.learning = factory.create_learning_repository()
        self.analytics = factory.create_analytics_repository()
        self.document_jobs = factory.create_document_job_repository()
        self.learning_resources = factory.create_learning_resource_repository()
        self.resource_sections = factory.create_resource_section_repository()
        self.resource_chunks = factory.create_resource_chunk_repository()
        self.knowledge_states = factory.create_knowledge_state_repository()

    def commit(self) -> None:
        # In-memory repositories just save instantly, so commit is a no-op.
        pass

    def rollback(self) -> None:
        # Rollback not supported for in-memory in this prototype.
        pass

    def close(self) -> None:
        pass
