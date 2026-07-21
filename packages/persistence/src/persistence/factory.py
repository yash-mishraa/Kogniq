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


class RepositoryFactory:
    """Factory to provide concrete repository implementations.
    Currently defaults to in-memory repositories. Future implementations
    like SQLite, Postgres, or Supabase will swap in here.
    """

    def __init__(self) -> None:
        self._document_repo = MemoryDocumentRepository()
        self._chunk_repo = MemoryChunkRepository()
        self._knowledge_repo = MemoryKnowledgeRepository()
        self._learning_repo = MemoryLearningRepository()

    def get_document_repository(self) -> AbstractDocumentRepository:
        return self._document_repo

    def get_chunk_repository(self) -> AbstractChunkRepository:
        return self._chunk_repo

    def get_knowledge_repository(self) -> AbstractKnowledgeRepository:
        return self._knowledge_repo

    def get_learning_repository(self) -> AbstractLearningRepository:
        return self._learning_repo
