import pytest
from backend.app import create_app
from backend.core.validators import DocumentValidator
from fastapi.testclient import TestClient


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
    return TestClient(app)


def test_process_document_success_md(client: TestClient) -> None:
    # Upload a tiny markdown file
    files = {"file": ("test.md", b"# Markdown Test", "text/markdown")}
    response = client.post("/api/v1/documents/process", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["filename"] == "test.md"
    assert data["chunk_count"] == 1
    assert data["embedding_count"] == 0
    assert data["knowledge_concepts"] == 0
    assert data["processor"] == "mock"
    assert data["processing_time_ms"] >= 0


def test_process_document_unsupported_extension(client: TestClient) -> None:
    # Unsupported image file
    files = {"file": ("test.jpg", b"imagebytes", "image/jpeg")}
    response = client.post("/api/v1/documents/process", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "unsupported_extension"


def test_process_document_empty_upload(client: TestClient) -> None:
    # Empty file
    files = {"file": ("test.txt", b"", "text/plain")}
    response = client.post("/api/v1/documents/process", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "empty_file"


def test_process_document_oversized(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # Temporarily lower the max size to 10 bytes
    monkeypatch.setattr(DocumentValidator, "MAX_SIZE_BYTES", 10)

    files = {"file": ("test.txt", b"this string is more than 10 bytes", "text/plain")}
    response = client.post("/api/v1/documents/process", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "file_too_large"


def test_process_document_pipeline_failure() -> None:
    from backend.dependencies import get_document_service

    class FailingMockService:
        def process_document(self, doc_input: object) -> None:
            _ = doc_input
            from backend.core.exceptions import BackendError

            raise BackendError("pipeline_execution_failed", "Simulated failure", 500)

    # Override dependency
    app = create_app()
    app.dependency_overrides[get_document_service] = lambda: FailingMockService()

    test_client = TestClient(app)
    files = {"file": ("test.txt", b"content", "text/plain")}
    response = test_client.post("/api/v1/documents/process", files=files)

    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "pipeline_execution_failed"
    assert data["error"]["message"] == "Simulated failure"
