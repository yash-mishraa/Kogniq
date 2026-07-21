import pytest
from backend.dependencies import (
    get_learning_service,
    get_pipeline_service,
    get_retrieval_service,
)
from backend.services.learning_service import LearningService
from backend.services.retrieval_service import RetrievalService
from backend.services.stubs import (
    StubPipelineService,
)


class MockAuthResult:
    def __init__(self, allowed: bool, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class MockAuthorizationService:
    async def require_permission(self, _user_id: str, _permission_id: str) -> MockAuthResult:
        return MockAuthResult(allowed=True, reason="")


@pytest.mark.asyncio
async def test_get_pipeline_service() -> None:
    service = await get_pipeline_service()
    assert isinstance(service, StubPipelineService)


@pytest.mark.asyncio
async def test_get_learning_service() -> None:
    service = await get_learning_service()
    assert isinstance(service, LearningService)


@pytest.mark.asyncio
async def test_get_retrieval_service() -> None:
    service = await get_retrieval_service()
    # We now use the real RetrievalService
    assert isinstance(service, RetrievalService)
