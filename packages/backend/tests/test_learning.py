import pytest
from backend.app import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    app = create_app()
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
