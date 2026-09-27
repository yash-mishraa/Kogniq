import pytest
from backend.core.validators import DocumentValidator
from backend.dependencies import get_authorization_service, get_document_service
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.app.config import APISettings
from apps.api.app.dependencies.auth import get_current_user
from apps.api.app.main import create_app
from auth.models import User
from shared.config import Environment


class MockAuthResult:
    def __init__(self, allowed: bool, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class MockAuthorizationService:
    async def require_permission(self, _user_id: str, _permission_id: str) -> MockAuthResult:
        return MockAuthResult(allowed=True, reason="")


@pytest.fixture
def test_app() -> FastAPI:
    settings = APISettings(
        environment=Environment.TEST,
        build="test",
        commit="test-commit",
        allowed_hosts=["testserver"],
        cors_origins=[],
    )
    app = create_app(settings)
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


@pytest.fixture
def auth_user() -> User:
    return User(user_id="user-123", email="user@test.com", display_name="User")


def test_process_document_success(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    class MockResult:
        status = "Uploaded"
        document_id = "doc-123"
        filename = "test.md"
        title = "Test"
        source = "test"
        processor = "markdown"
        chunk_count = 1
        processing_time_ms = 100
        warnings: tuple[str, ...] = ()

    class MockService:
        async def prepare_document(self, _doc_input: object) -> MockResult:
            return MockResult()

        async def run_document_pipeline(self, _doc_input: object, document_id: str) -> None:
            pass

    test_app.dependency_overrides[get_document_service] = lambda: MockService()
    test_app.dependency_overrides[get_current_user] = lambda: auth_user

    files = {"file": ("test.md", b"# Markdown Test", "text/markdown")}
    response = client.post("/api/v1/documents/process", files=files)

    assert response.status_code == 200
    assert response.json()["status"] == "Uploaded"


def test_process_document_no_file(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    response = client.post("/api/v1/documents/process")
    assert response.status_code == 422


def test_process_document_validation_error(
    client: TestClient, test_app: FastAPI, auth_user: User
) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    # Empty file
    files = {"file": ("test.md", b"", "text/markdown")}
    response = client.post("/api/v1/documents/process", files=files)
    assert response.status_code == 400


def test_process_document_unsupported_type(
    client: TestClient, test_app: FastAPI, auth_user: User
) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    files = {"file": ("test.exe", b"binary", "application/x-msdownload")}
    response = client.post("/api/v1/documents/process", files=files)
    assert response.status_code == 400


def test_process_document_oversized(
    client: TestClient, test_app: FastAPI, auth_user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    # Temporarily lower the max size to 10 bytes
    monkeypatch.setattr(DocumentValidator, "MAX_SIZE_BYTES", 10)

    files = {"file": ("test.txt", b"this string is more than 10 bytes", "text/plain")}
    response = client.post("/api/v1/documents/process", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "file_too_large"


def test_recover_failed_jobs_endpoint(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    
    from backend.dependencies import get_uow_factory
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)
    
    from persistence.models import DocumentJob
    from datetime import datetime, UTC
    
    with uow_factory().create() as uow:
        uow.document_jobs.save(DocumentJob(
            id="job-api-1", user_id=auth_user.user_id, filename="test.pdf", status="Error", created_at=datetime.now(UTC)
        ))
        uow.document_jobs.save(DocumentJob(
            id="job-api-2", user_id="other-user", filename="test2.pdf", status="Error", created_at=datetime.now(UTC)
        ))
    
    response = client.post("/api/v1/documents/recover")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["recovered_count"] == 1
    
    with uow_factory().create() as uow:
        assert uow.document_jobs.get("job-api-1") is None
        assert uow.document_jobs.get("job-api-2") is not None
        
    test_app.dependency_overrides.pop(get_current_user)
    unauth_response = client.post("/api/v1/documents/recover")
    assert unauth_response.status_code == 401
