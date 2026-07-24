import os
from pathlib import Path

import pytest

from application.document.commands import ProcessDocumentCommand
from application.document.process_document import ProcessDocumentUseCase
from application.exceptions import ApplicationError


def test_no_fastapi_imports() -> None:
    """Verify that the application layer has no FastAPI/Starlette/Pydantic imports."""
    application_dir = Path(__file__).parent.parent / "src" / "application"

    for root, _, files in os.walk(application_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = Path(root) / file
            with path.open(encoding="utf-8") as f:
                content = f.read()
                assert "fastapi" not in content, f"FastAPI import found in {path}"
                assert "starlette" not in content, f"Starlette import found in {path}"
                assert "pydantic" not in content, f"Pydantic import found in {path}"
                assert "backend.schemas" not in content, f"Backend schema import found in {path}"


class MockAuthResult:
    def __init__(self, allowed: bool, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class MockAuthorizationService:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed

    async def require_permission(self, user_id: str, permission_id: str) -> MockAuthResult:
        _ = user_id
        _ = permission_id
        return MockAuthResult(allowed=self.allowed, reason="Mock reason")

    async def assign_role(self, user_id: str, role_id: str) -> None:
        pass


class MockDocumentService:
    class MockResult:
        status = "completed"
        document_id = "doc1"
        filename = "test.txt"
        title = "Test Title"
        source = "test"
        processor = "mock"
        chunk_count = 1
        embedding_count = 1
        knowledge_concepts = 1
        knowledge_relationships = 1
        processing_time_ms = 100.0

        def __init__(self) -> None:
            self.warnings: list[str] = []

    async def process_document(self, command: object) -> MockResult:
        _ = command
        return self.MockResult()


class FailingDocumentService:
    async def process_document(self, command: object) -> None:
        _ = command
        raise ValueError("Downstream failure")


@pytest.mark.asyncio
async def test_process_document_success() -> None:
    use_case = ProcessDocumentUseCase(
        auth_service=None,  # type: ignore
        authorization_service=MockAuthorizationService(allowed=True),
        document_service=MockDocumentService(),
    )
    cmd = ProcessDocumentCommand(
        user_id="user1",
        filename="test.txt",
        content_type="text/plain",
        size_bytes=10,
        content=b"test",
    )
    result = await use_case.execute(cmd)

    assert result.status == "completed"
    assert result.document_id == "doc1"
    assert result.filename == "test.txt"


@pytest.mark.asyncio
async def test_process_document_unauthorized() -> None:
    use_case = ProcessDocumentUseCase(
        auth_service=None,  # type: ignore
        authorization_service=MockAuthorizationService(allowed=False),
        document_service=MockDocumentService(),
    )
    cmd = ProcessDocumentCommand(
        user_id="user1",
        filename="test.txt",
        content_type="text/plain",
        size_bytes=10,
        content=b"test",
    )

    with pytest.raises(ApplicationError) as exc:
        await use_case.execute(cmd)
    assert "Permission denied" in str(exc.value)


@pytest.mark.asyncio
async def test_process_document_downstream_failure() -> None:
    use_case = ProcessDocumentUseCase(
        auth_service=None,  # type: ignore
        authorization_service=MockAuthorizationService(allowed=True),
        document_service=FailingDocumentService(),
    )
    cmd = ProcessDocumentCommand(
        user_id="user1",
        filename="test.txt",
        content_type="text/plain",
        size_bytes=10,
        content=b"test",
    )

    with pytest.raises(ValueError) as exc:
        await use_case.execute(cmd)
    assert "Downstream failure" in str(exc.value)
