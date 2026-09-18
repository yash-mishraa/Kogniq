import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from apps.api.app.dependencies.auth import get_current_user
from backend.dependencies import (
    get_get_learning_resource_use_case,
    get_list_learning_resources_use_case,
    get_resource_sections_use_case,
    get_resource_chunks_use_case,
    get_resource_statistics_use_case,
)
from auth.models import User
from content.domain.entities import LearningResource, ResourceSection, ResourceChunk
from content.domain.enums import ProcessingStatus, ResourceType
from fastapi import FastAPI

@pytest.fixture
def auth_user() -> User:
    return User(user_id="user-123", email="user@test.com", display_name="User")

@pytest.fixture
def override_auth(client: TestClient, auth_user: User) -> None:
    client.app.dependency_overrides[get_current_user] = lambda: auth_user  # type: ignore

@pytest.fixture
def list_uc() -> AsyncMock:
    mock = AsyncMock()
    mock.execute.return_value = [
        LearningResource(id="r1", title="Doc", resource_type=ResourceType.TEXT, source="src", status=ProcessingStatus.PROCESSED, checksum="hash")
    ]
    return mock

@pytest.fixture
def get_uc() -> AsyncMock:
    mock = AsyncMock()
    mock.execute.return_value = LearningResource(id="r1", title="Doc", resource_type=ResourceType.TEXT, source="src", status=ProcessingStatus.PROCESSED, checksum="hash")
    return mock

@pytest.fixture
def sections_uc() -> AsyncMock:
    mock = AsyncMock()
    mock.execute.return_value = [ResourceSection(id="s1", resource_id="r1", title="Sec", order=0)]
    return mock

@pytest.fixture
def chunks_uc() -> AsyncMock:
    mock = AsyncMock()
    mock.execute.return_value = [ResourceChunk(id="c1", resource_id="r1", section_id="s1", text="Text", order=0, checksum="hash")]
    return mock

@pytest.fixture
def stats_uc() -> AsyncMock:
    mock = AsyncMock()
    mock.execute.return_value = {"section_count": 1, "chunk_count": 1, "total_tokens": 10}
    return mock

def test_list_resources(client: TestClient, override_auth: None, list_uc: AsyncMock) -> None:
    client.app.dependency_overrides[get_list_learning_resources_use_case] = lambda: list_uc  # type: ignore
    response = client.get("/api/v1/resources")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_resource(client: TestClient, override_auth: None, get_uc: AsyncMock) -> None:
    client.app.dependency_overrides[get_get_learning_resource_use_case] = lambda: get_uc  # type: ignore
    response = client.get("/api/v1/resources/r1")
    assert response.status_code == 200
    assert response.json()["id"] == "r1"

def test_get_sections(client: TestClient, override_auth: None, sections_uc: AsyncMock) -> None:
    client.app.dependency_overrides[get_resource_sections_use_case] = lambda: sections_uc  # type: ignore
    response = client.get("/api/v1/resources/r1/sections")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_chunks(client: TestClient, override_auth: None, chunks_uc: AsyncMock) -> None:
    client.app.dependency_overrides[get_resource_chunks_use_case] = lambda: chunks_uc  # type: ignore
    response = client.get("/api/v1/resources/r1/chunks")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_statistics(client: TestClient, override_auth: None, stats_uc: AsyncMock) -> None:
    client.app.dependency_overrides[get_resource_statistics_use_case] = lambda: stats_uc  # type: ignore
    response = client.get("/api/v1/resources/r1/statistics")
    assert response.status_code == 200
    assert response.json()["total_tokens"] == 10
