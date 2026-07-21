from typing import Annotated

from fastapi import Depends
from persistence.factory import RepositoryFactory

from backend.core.settings import settings
from backend.services.context_provider import LearningContextProvider
from backend.services.document_service import DocumentService
from backend.services.generator_factory import GeneratorFactory
from backend.services.job_service import JobService
from backend.services.learning_service import LearningService
from backend.services.retrieval_factory import RetrievalFactory
from backend.services.retrieval_service import RetrievalService
from backend.services.stubs import (
    PipelineService,
    StubPipelineService,
)
from jobs.interfaces import AbstractJobManager
from jobs.memory import MemoryJobManager

# In the future, these dependencies will construct the real implementations
# or pull them from an application-level container.


class _JobManagerSingleton:
    _instance: AbstractJobManager | None = None

    @classmethod
    def get(cls) -> AbstractJobManager:
        if cls._instance is None:
            cls._instance = MemoryJobManager()
        return cls._instance


_repository_factory_instance: RepositoryFactory | None = None


def get_repository_factory() -> RepositoryFactory:
    global _repository_factory_instance
    # Use a singleton for now to share the in-memory state across requests.
    if _repository_factory_instance is None:
        _repository_factory_instance = RepositoryFactory()
    return _repository_factory_instance


_retrieval_factory_instance: RetrievalFactory | None = None


def get_retrieval_factory() -> RetrievalFactory:
    global _retrieval_factory_instance
    if _retrieval_factory_instance is None:
        _retrieval_factory_instance = RetrievalFactory(settings)
    return _retrieval_factory_instance


async def get_pipeline_service() -> PipelineService:
    return StubPipelineService()


async def get_learning_service() -> LearningService:
    repo_factory = get_repository_factory()
    context_provider = LearningContextProvider(repository_factory=repo_factory)
    factory = GeneratorFactory()

    return LearningService(
        context_provider=context_provider,
        generator_factory=factory,
        repository_factory=repo_factory,
    )


async def get_retrieval_service() -> RetrievalService:
    retrieval_factory = get_retrieval_factory()
    repo_factory = get_repository_factory()

    return RetrievalService(
        retriever=retrieval_factory.get_retriever(),
        chunk_repository=repo_factory.get_chunk_repository(),
    )


# -----------------
# Core Services
# -----------------


async def get_document_service() -> "DocumentService":
    from backend.services.document_service import DocumentService
    from backend.services.pipeline_factory import PipelineFactory

    pipeline = PipelineFactory.create()
    repo_factory = get_repository_factory()
    return DocumentService(pipeline=pipeline, repository_factory=repo_factory)


def get_job_manager() -> AbstractJobManager:
    return _JobManagerSingleton.get()


async def get_job_service() -> JobService:
    job_manager = get_job_manager()
    document_service = await get_document_service()
    return JobService(job_manager=job_manager, document_service=document_service)





# Typed dependencies for clean injection in route handlers
PipelineDependency = Annotated[PipelineService, Depends(get_pipeline_service)]
LearningDependency = Annotated[LearningService, Depends(get_learning_service)]
RetrievalDependency = Annotated[RetrievalService, Depends(get_retrieval_service)]
JobDependency = Annotated[JobService, Depends(get_job_service)]
