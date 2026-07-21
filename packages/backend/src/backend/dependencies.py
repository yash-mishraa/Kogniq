from typing import Annotated

from fastapi import Depends

from backend.services.context_provider import LearningContextProvider
from backend.services.document_service import DocumentService
from backend.services.generator_factory import GeneratorFactory
from backend.services.learning_service import LearningService
from backend.services.stubs import (
    PipelineService,
    RetrievalService,
    StubPipelineService,
    StubRetrievalService,
)

# In the future, these dependencies will construct the real implementations
# or pull them from an application-level container.


async def get_pipeline_service() -> PipelineService:
    return StubPipelineService()


async def get_learning_service() -> LearningService:
    context_provider = LearningContextProvider()
    factory = GeneratorFactory()

    return LearningService(context_provider=context_provider, generator_factory=factory)


async def get_retrieval_service() -> RetrievalService:
    return StubRetrievalService()


# -----------------
# Core Services
# -----------------


async def get_document_service() -> "DocumentService":
    from backend.services.document_service import DocumentService
    from backend.services.pipeline_factory import PipelineFactory

    pipeline = PipelineFactory.create()
    return DocumentService(pipeline=pipeline)


# Typed dependencies for clean injection in route handlers
PipelineDependency = Annotated[PipelineService, Depends(get_pipeline_service)]
LearningDependency = Annotated[LearningService, Depends(get_learning_service)]
RetrievalDependency = Annotated[RetrievalService, Depends(get_retrieval_service)]
