import pytest
from backend.dependencies import (
    get_learning_service,
    get_pipeline_service,
    get_retrieval_service,
)
from backend.services.stubs import (
    StubLearningService,
    StubPipelineService,
    StubRetrievalService,
)


@pytest.mark.asyncio
async def test_get_pipeline_service() -> None:
    service = await get_pipeline_service()
    assert isinstance(service, StubPipelineService)


@pytest.mark.asyncio
async def test_get_learning_service() -> None:
    service = await get_learning_service()
    assert isinstance(service, StubLearningService)


@pytest.mark.asyncio
async def test_get_retrieval_service() -> None:
    service = await get_retrieval_service()
    assert isinstance(service, StubRetrievalService)
