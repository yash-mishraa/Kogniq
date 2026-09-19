# type: ignore
from unittest.mock import AsyncMock

import pytest

from application.exceptions import ApplicationError
from application.resources.use_cases import (
    GetLearningResourceUseCase,
    GetResourceChunksUseCase,
    GetResourceSectionsUseCase,
    GetResourceStatisticsUseCase,
    ListLearningResourcesUseCase,
)
from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from content.domain.enums import ProcessingStatus, ResourceType


class FakeAuthService:
    async def get_current_user(self, session_id):
        return AsyncMock(user_id="user-1")

    async def register(self, email, password, display_name) -> None:
        pass


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.learning_resources = AsyncMock()
        self.resource_sections = AsyncMock()
        self.resource_chunks = AsyncMock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FakeUoWFactory:
    def __init__(self) -> None:
        self.uow = FakeUnitOfWork()

    def create(self):
        return self.uow


@pytest.fixture
def uow_factory():
    return FakeUoWFactory()


@pytest.fixture
def auth_service():
    return FakeAuthService()


@pytest.mark.asyncio
async def test_get_resource(auth_service, uow_factory) -> None:
    uc = GetLearningResourceUseCase(auth_service, uow_factory)

    resource = LearningResource(
        id="r1",
        title="T",
        resource_type=ResourceType.TEXT,
        source="src",
        status=ProcessingStatus.PROCESSED,
        checksum="hash",
    )
    uow_factory.uow.learning_resources.get.return_value = resource

    res = await uc.execute("user-1", "r1")
    assert res.id == "r1"
    uow_factory.uow.learning_resources.get.assert_called_with(resource_id="r1", user_id="user-1")


@pytest.mark.asyncio
async def test_get_resource_not_found(auth_service, uow_factory) -> None:
    uc = GetLearningResourceUseCase(auth_service, uow_factory)
    uow_factory.uow.learning_resources.get.return_value = None

    with pytest.raises(ApplicationError, match="not found"):
        await uc.execute("user-1", "r1")


@pytest.mark.asyncio
async def test_list_resources(auth_service, uow_factory) -> None:
    uc = ListLearningResourcesUseCase(auth_service, uow_factory)

    resource = LearningResource(
        id="r1",
        title="T",
        resource_type=ResourceType.TEXT,
        source="src",
        status=ProcessingStatus.PROCESSED,
        checksum="hash",
    )
    uow_factory.uow.learning_resources.list.return_value = [resource]

    res = await uc.execute("user-1", limit=10, offset=0)
    assert len(res) == 1
    assert res[0].id == "r1"


@pytest.mark.asyncio
async def test_get_sections(auth_service, uow_factory) -> None:
    uc = GetResourceSectionsUseCase(auth_service, uow_factory)

    section = ResourceSection(id="s1", resource_id="r1", title="S", order=0)
    uow_factory.uow.resource_sections.get_by_resource.return_value = [section]

    res = await uc.execute("user-1", "r1")
    assert len(res) == 1
    assert res[0].id == "s1"


@pytest.mark.asyncio
async def test_get_sections_not_found(auth_service, uow_factory) -> None:
    uc = GetResourceSectionsUseCase(auth_service, uow_factory)
    uow_factory.uow.resource_sections.get_by_resource.return_value = []
    uow_factory.uow.learning_resources.get.return_value = None

    with pytest.raises(ApplicationError, match="not found"):
        await uc.execute("user-1", "r1")


@pytest.mark.asyncio
async def test_get_chunks(auth_service, uow_factory) -> None:
    uc = GetResourceChunksUseCase(auth_service, uow_factory)

    chunk = ResourceChunk(
        id="c1", resource_id="r1", section_id="s1", text="text", order=0, checksum="123"
    )
    uow_factory.uow.resource_chunks.get_by_resource.return_value = [chunk]

    res = await uc.execute("user-1", "r1")
    assert len(res) == 1
    assert res[0].id == "c1"


@pytest.mark.asyncio
async def test_get_statistics(auth_service, uow_factory) -> None:
    uc = GetResourceStatisticsUseCase(auth_service, uow_factory)

    resource = LearningResource(
        id="r1",
        title="T",
        resource_type=ResourceType.TEXT,
        source="src",
        status=ProcessingStatus.PROCESSED,
        checksum="hash",
    )
    uow_factory.uow.learning_resources.get.return_value = resource

    section = ResourceSection(id="s1", resource_id="r1", title="S", order=0)
    ResourceChunk(
        id="c1",
        resource_id="r1",
        section_id="s1",
        text="text",
        order=0,
        checksum="123",
        token_estimate=5,
    )

    uow_factory.uow.resource_sections.get_by_resource.return_value = [section, section]
    uow_factory.uow.resource_chunks.statistics_by_resource.return_value = {
        "chunk_count": 3,
        "total_tokens": 15,
    }

    res = await uc.execute("user-1", "r1")
    assert res["section_count"] == 2
    assert res["chunk_count"] == 3
    assert res["total_tokens"] == 15
