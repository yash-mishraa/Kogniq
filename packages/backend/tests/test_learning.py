import asyncio
from datetime import UTC, datetime

import pytest
from backend.app import create_app
from backend.dependencies import get_repository_factory
from fastapi.testclient import TestClient
from knowledge.graph import KnowledgeGraph

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics


class MockAuthResult:
    def __init__(self, allowed: bool, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class MockAuthorizationService:
    async def require_permission(self, _user_id: str, _permission_id: str) -> MockAuthResult:
        return MockAuthResult(allowed=True, reason="")


@pytest.fixture
def client() -> TestClient:
    app = create_app()

    factory = get_repository_factory()
    chunk_repo = factory.get_chunk_repository()
    know_repo = factory.get_knowledge_repository()

    async def seed() -> None:
        chunk = Chunk(
            id="chunk-test-1",
            document_id="test-doc-123",
            chunk_index=0,
            text="Simulated chunk content for testing.",
            metadata=ChunkMetadata(
                processor="mock", document_version="v1", source="mock", checksum="123"
            ),
            statistics=ChunkStatistics(
                character_count=36,
                line_count=1,
                word_count=5,
                estimated_tokens=10,
                processing_timestamp=datetime.now(UTC),
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        )
        await chunk_repo.save(ChunkCollection(chunks=(chunk,)))
        await know_repo.save("test-doc-123", KnowledgeGraph(concepts=(), relationships=()))

    asyncio.run(seed())

    return TestClient(app)


@pytest.mark.parametrize(
    "generator_name", ["summary", "notes", "flashcards", "quiz", "explanation", "study_guide"]
)
def test_learning_generation_success(client: TestClient, generator_name: str) -> None:
    request_data = {"document_id": "test-doc-123", "generator": generator_name}
    response = client.post("/api/v1/learning/generate", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["generator"] == generator_name
    assert data["document_id"] == "test-doc-123"
    assert "title" in data
    assert "generated_content" in data
    assert "metadata" in data
    assert "statistics" in data


def test_learning_generation_unsupported_generator(client: TestClient) -> None:
    request_data = {"document_id": "test-doc-123", "generator": "invalid_generator"}
    response = client.post("/api/v1/learning/generate", json=request_data)

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "unsupported_generator"


def test_learning_generation_missing_document_id(client: TestClient) -> None:
    request_data = {"document_id": "", "generator": "summary"}
    response = client.post("/api/v1/learning/generate", json=request_data)

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "invalid_request"


def test_learning_generation_unsupported_document_id(client: TestClient) -> None:
    request_data = {"document_id": "unsupported", "generator": "summary"}
    response = client.post("/api/v1/learning/generate", json=request_data)

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "document_not_found"


def test_learning_generation_factory_failure() -> None:
    from backend.dependencies import get_learning_service

    class FailingContextMockService:
        def generate_artifact(self, request: object) -> None:
            _ = request
            from backend.core.exceptions import BackendError

            raise BackendError("generation_failed", "Simulated failure", 500)

    app = create_app()
    app.dependency_overrides[get_learning_service] = lambda: FailingContextMockService()

    test_client = TestClient(app)
    response = test_client.post(
        "/api/v1/learning/generate", json={"document_id": "doc1", "generator": "summary"}
    )

    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "generation_failed"
