from datetime import UTC, datetime

import pytest
from backend.app import create_app
from backend.dependencies import (
    get_authorization_service,
    get_retrieve_use_case,
    get_uow_factory,
)
from backend.services.retrieval_service import RetrievalService
from fastapi.testclient import TestClient
from retrieval.exceptions import RetrievalError
from retrieval.interfaces import AbstractRetriever
from retrieval.models import RetrievalQuery, RetrievalResult

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


class MockRetriever(AbstractRetriever):
    def __init__(self, results: list[RetrievalResult], should_fail: bool = False) -> None:
        self._results = results
        self.should_fail = should_fail
        self.last_query: RetrievalQuery | None = None

    def retrieve(self, query: RetrievalQuery) -> tuple[RetrievalResult, ...]:
        self.last_query = query
        if self.should_fail:
            raise RetrievalError("Mocked retriever failure")
        return tuple(self._results)


@pytest.fixture
def mock_chunks() -> ChunkCollection:
    chunks = [
        Chunk(
            id=f"chunk-{i}",
            document_id="test-doc",
            chunk_index=i,
            text=f"Mock content {i}",
            metadata=ChunkMetadata(
                processor="mock", document_version="v1", source="mock", checksum="123"
            ),
            statistics=ChunkStatistics(
                character_count=10,
                line_count=1,
                word_count=2,
                estimated_tokens=2,
                processing_timestamp=datetime.now(UTC),
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        )
        for i in range(10)
    ]
    return ChunkCollection(chunks=tuple(chunks))


@pytest.fixture
def mock_results() -> list[RetrievalResult]:
    return [
        RetrievalResult(
            query_id="q1",
            query_text="query",
            embedding_id=f"emb-{i}",
            chunk_id=f"chunk-{i}",
            similarity_score=0.9 - (i * 0.05),
            provider="mock",
            model="mock",
        )
        for i in range(5)
    ]


@pytest.fixture
def client_with_mocks(
    mock_chunks: ChunkCollection, mock_results: list[RetrievalResult]
) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()

    uow_factory = get_uow_factory()
    import asyncio

    async def seed() -> None:
        with uow_factory.create() as uow:
            await uow.chunks.save(mock_chunks)

    asyncio.run(seed())

    retriever = MockRetriever(mock_results)
    mock_service = RetrievalService(
        retriever=retriever,
        uow_factory=uow_factory,
    )

    from unittest.mock import MagicMock

    from application.retrieval.retrieve import RetrieveUseCase

    authz_svc = MockAuthorizationService()
    use_case = RetrieveUseCase(
        auth_service=MagicMock(), authorization_service=authz_svc, retrieval_service=mock_service
    )

    app.dependency_overrides[get_retrieve_use_case] = lambda: use_case

    return TestClient(app)


def test_retrieval_success(client_with_mocks: TestClient) -> None:
    request_data = {"document_id": "test-doc", "query": "gradient descent", "top_k": 3}
    response = client_with_mocks.post("/api/v1/retrieval/search", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["total_results"] == 3
    assert len(data["results"]) == 3
    assert data["results"][0]["chunk_id"] == "chunk-0"
    assert data["results"][0]["similarity_score"] == 0.9
    assert data["results"][0]["chunk_text"] == "Mock content 0"
    assert "processor" in data["results"][0]["metadata"]


def test_retrieval_empty_query(client_with_mocks: TestClient) -> None:
    request_data = {"document_id": "test-doc", "query": "", "top_k": 3}
    response = client_with_mocks.post("/api/v1/retrieval/search", json=request_data)

    assert response.status_code == 422  # Pydantic validation error


def test_retrieval_invalid_document_id(client_with_mocks: TestClient) -> None:
    request_data = {"document_id": "missing-doc", "query": "gradient descent"}
    response = client_with_mocks.post("/api/v1/retrieval/search", json=request_data)

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "document_not_found"


def test_retrieval_similarity_threshold(client_with_mocks: TestClient) -> None:
    request_data = {"document_id": "test-doc", "query": "test", "minimum_similarity": 0.85}
    response = client_with_mocks.post("/api/v1/retrieval/search", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # Scores: chunk-0: 0.9, chunk-1: 0.85, chunk-2: 0.8.
    # threshold 0.85 means chunk-0 and chunk-1 should be returned.
    assert data["total_results"] == 2
    assert "warnings" in data
    assert any("filtered out" in w for w in data["warnings"])


def test_retrieval_top_k_larger_than_available(client_with_mocks: TestClient) -> None:
    # We have 5 mock results, but request top_k=20
    request_data = {"document_id": "test-doc", "query": "test", "top_k": 20}
    response = client_with_mocks.post("/api/v1/retrieval/search", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 5
    assert len(data["results"]) == 5


def test_retrieval_chunk_repository_miss() -> None:
    # Retriever returns chunk-99 which is not in the document.
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    uow_factory = get_uow_factory()

    bad_results = [
        RetrievalResult(
            query_id="q1",
            query_text="test",
            embedding_id="emb-99",
            chunk_id="chunk-99",
            similarity_score=0.9,
            provider="mock",
            model="mock",
        )
    ]
    retriever = MockRetriever(bad_results)
    mock_service = RetrievalService(
        retriever=retriever,
        uow_factory=uow_factory,
    )
    from unittest.mock import MagicMock

    from application.retrieval.retrieve import RetrieveUseCase

    auth_svc = MagicMock()
    authz_svc = MockAuthorizationService()
    use_case = RetrieveUseCase(
        auth_service=auth_svc, authorization_service=authz_svc, retrieval_service=mock_service
    )
    app.dependency_overrides[get_retrieve_use_case] = lambda: use_case

    client = TestClient(app)
    request_data = {"document_id": "test-doc", "query": "test"}
    response = client.post("/api/v1/retrieval/search", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 0
    assert len(data["results"]) == 0
    assert any("filtered out" in w for w in data["warnings"])


def test_retriever_exception_translation() -> None:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    uow_factory = get_uow_factory()

    retriever = MockRetriever([], should_fail=True)
    mock_service = RetrievalService(
        retriever=retriever,
        uow_factory=uow_factory,
    )
    from unittest.mock import MagicMock

    from application.retrieval.retrieve import RetrieveUseCase

    auth_svc = MagicMock()
    authz_svc = MockAuthorizationService()
    use_case = RetrieveUseCase(
        auth_service=auth_svc, authorization_service=authz_svc, retrieval_service=mock_service
    )
    app.dependency_overrides[get_retrieve_use_case] = lambda: use_case

    client = TestClient(app)
    request_data = {"document_id": "test-doc", "query": "test"}
    response = client.post("/api/v1/retrieval/search", json=request_data)

    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "retrieval_failed"
    assert "Mocked retriever failure" in data["error"]["message"]
