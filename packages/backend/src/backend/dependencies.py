from typing import Annotated

from fastapi import Depends

from backend.services.stubs import (
    LearningService,
    PipelineService,
    RetrievalService,
    StubLearningService,
    StubPipelineService,
    StubRetrievalService,
)

# In the future, these dependencies will construct the real implementations
# or pull them from an application-level container.


async def get_pipeline_service() -> PipelineService:
    return StubPipelineService()


async def get_learning_service() -> LearningService:
    return StubLearningService()


async def get_retrieval_service() -> RetrievalService:
    return StubRetrievalService()


# Typed dependencies for clean injection in route handlers
PipelineDependency = Annotated[PipelineService, Depends(get_pipeline_service)]
LearningDependency = Annotated[LearningService, Depends(get_learning_service)]
RetrievalDependency = Annotated[RetrievalService, Depends(get_retrieval_service)]
