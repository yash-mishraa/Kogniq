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
def test_get_document_structured_pages(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.page import NormalizedPage
    from content.normalized.block import NormalizedBlock
    from content.normalized.enums import BlockType
    from datetime import datetime, UTC
    import asyncio
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-123"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id,
                title="Structured Document",
                source="test",
                checksum="test",
                version="1.0",
                created_at=datetime.now(UTC),
                user_id=auth_user.user_id,
                pages=(
                    NormalizedPage(
                        page_number=1,
                        width=800.0,
                        height=600.0,
                        blocks=(
                            NormalizedBlock(
                                block_id="b1",
                                block_type=BlockType.PARAGRAPH,
                                text="Hello World",
                                bbox=(10, 10, 100, 20),
                                order=0
                            ),
                        )
                    ),
                )
            )
            await uow.documents.save(doc)

        response = client.get(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Ready"
        assert data["pages"] is not None
        assert len(data["pages"]) == 1
        
        page = data["pages"][0]
        assert page["page_number"] == 1
        assert page["width"] == 800.0
        assert page["height"] == 600.0
        assert len(page["blocks"]) == 1
        
        block = page["blocks"][0]
        assert block["id"] == "b1"
        assert block["text"] == "Hello World"
        assert block["type"] == "PARAGRAPH"
        assert block["bbox"] == [10.0, 10.0, 100.0, 20.0]
    
    asyncio.run(run_test())

def test_get_document_file_success(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.page import NormalizedPage
    from datetime import datetime, UTC
    import asyncio
    import os
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-file-123"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id,
                title="File Doc",
                source="test",
                checksum="test",
                version="1.0",
                created_at=datetime.now(UTC),
                user_id=auth_user.user_id,
                pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)

        # Create dummy file
        upload_dir = os.path.join("data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{doc_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(b"%PDF-1.4 fake pdf content")

        response = client.get(f"/api/v1/documents/{doc_id}/file")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content == b"%PDF-1.4 fake pdf content"
        
    asyncio.run(run_test())

def test_get_document_file_cross_user_denial(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.page import NormalizedPage
    from datetime import datetime, UTC
    import asyncio
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-file-other-user"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id,
                title="Other File Doc",
                source="test",
                checksum="test",
                version="1.0",
                created_at=datetime.now(UTC),
                user_id="different-user-id",
                pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)

        response = client.get(f"/api/v1/documents/{doc_id}/file")
        assert response.status_code == 403
        
    asyncio.run(run_test())

def test_get_document_file_missing_on_disk(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.page import NormalizedPage
    from datetime import datetime, UTC
    import asyncio
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-missing-file"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id,
                title="Missing File Doc",
                source="test",
                checksum="test",
                version="1.0",
                created_at=datetime.now(UTC),
                user_id=auth_user.user_id,
                pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)

        response = client.get(f"/api/v1/documents/{doc_id}/file")
        assert response.status_code == 404
        
    asyncio.run(run_test())

def test_get_document_semantics(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.semantics import DocumentSemantics
    from datetime import datetime, UTC
    import asyncio
    import json
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-semantics"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id, title="Doc", source="test", checksum="test", version="1.0",
                created_at=datetime.now(UTC), user_id=auth_user.user_id, pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)
            
            semantics = DocumentSemantics(
                id="sem-1", document_id=doc_id, semantic_version="2", status="ready", is_active=True,
                semantics_json=json.dumps({"sections": [{"id": "sec1", "title": "Intro", "page_number": 1, "level": 1}], "figures": []}),
                created_at=datetime.now(UTC), completed_at=datetime.now(UTC)
            )
            await uow.semantics.save(semantics)

        response = client.get(f"/api/v1/documents/{doc_id}/semantics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["semantic_version"] == "2"
        assert len(data["sections"]) == 1
        assert data["sections"][0]["title"] == "Intro"

    asyncio.run(run_test())

def test_get_document_semantics_cross_user(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from datetime import datetime, UTC
    import asyncio
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-semantics-cross"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id, title="Doc", source="test", checksum="test", version="1.0",
                created_at=datetime.now(UTC), user_id="other-user", pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)
            
        response = client.get(f"/api/v1/documents/{doc_id}/semantics")
        assert response.status_code == 403

    asyncio.run(run_test())

def test_get_document_semantics_unavailable(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.semantics import DocumentSemantics
    from datetime import datetime, UTC
    import asyncio
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-semantics-unavailable"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id, title="Doc", source="test", checksum="test", version="1.0",
                created_at=datetime.now(UTC), user_id=auth_user.user_id, pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)
            
            # Save failed version
            semantics = DocumentSemantics(
                id="sem-failed", document_id=doc_id, semantic_version="2", status="failed", is_active=True,
                semantics_json="", created_at=datetime.now(UTC), completed_at=datetime.now(UTC)
            )
            await uow.semantics.save(semantics)

        response = client.get(f"/api/v1/documents/{doc_id}/semantics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"
        assert len(data["sections"]) == 0

    asyncio.run(run_test())
def test_get_document_semantics_malformed(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.semantics import DocumentSemantics
    from datetime import datetime, UTC
    import asyncio
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-semantics-malformed"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id, title="Doc", source="test", checksum="test", version="1.0",
                created_at=datetime.now(UTC), user_id=auth_user.user_id, pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)
            
            semantics = DocumentSemantics(
                id="sem-malformed", document_id=doc_id, semantic_version="2", status="ready", is_active=True,
                semantics_json="{malformed_json", created_at=datetime.now(UTC), completed_at=datetime.now(UTC)
            )
            await uow.semantics.save(semantics)

        response = client.get(f"/api/v1/documents/{doc_id}/semantics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"
        assert len(data["sections"]) == 0

    asyncio.run(run_test())

def test_get_document_semantics_structurally_invalid(client: TestClient, test_app: FastAPI, auth_user: User) -> None:
    test_app.dependency_overrides[get_current_user] = lambda: auth_user
    from backend.dependencies import get_uow_factory
    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    from content.normalized.semantics import DocumentSemantics
    from datetime import datetime, UTC
    import asyncio
    
    uow_factory = test_app.dependency_overrides.get(get_uow_factory, get_uow_factory)()
    doc_id = "test-doc-semantics-invalid"
    
    async def run_test():
        with uow_factory.create() as uow:
            doc = NormalizedDocument(
                id=doc_id, title="Doc", source="test", checksum="test", version="1.0",
                created_at=datetime.now(UTC), user_id=auth_user.user_id, pages=(NormalizedPage(page_number=1, blocks=()),)
            )
            await uow.documents.save(doc)
            
            invalid_json = """{"sections": [{"page_number": "not-an-integer"}], "figures": []}"""
            semantics = DocumentSemantics(
                id="sem-invalid", document_id=doc_id, semantic_version="2", status="ready", is_active=True,
                semantics_json=invalid_json, created_at=datetime.now(UTC), completed_at=datetime.now(UTC)
            )
            await uow.semantics.save(semantics)

        response = client.get(f"/api/v1/documents/{doc_id}/semantics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"

    asyncio.run(run_test())
