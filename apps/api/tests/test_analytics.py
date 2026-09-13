import pytest
from fastapi.testclient import TestClient

from apps.api.app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()

    class MockSession:
        user_id = "user-123"

    class MockAuthService:
        async def validate_session(self, token: str) -> MockSession | None:
            if token == "session-123":
                return MockSession()
            return None

    from backend.dependencies import get_authentication_service, get_uow_factory

    app.dependency_overrides[get_authentication_service] = lambda: MockAuthService()

    uow_factory = get_uow_factory()
    import asyncio

    async def seed() -> None:
        from datetime import UTC, datetime

        from content.normalized.document import NormalizedDocument
        from content.normalized.page import NormalizedPage

        doc = NormalizedDocument(
            id="doc-1",
            title="test",
            source="test",
            checksum="1",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-123",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc)

    asyncio.run(seed())

    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer session-123"}


def test_record_event_quiz(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/analytics/events",
        headers=auth_headers,
        json={
            "event_id": "quiz-123",
            "event_type": "quiz_completed",
            "document_id": "doc-1",
            "data": {"score": 3, "total_questions": 4},
        },
    )
    assert response.status_code == 204


def test_record_event_flashcard(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/analytics/events",
        headers=auth_headers,
        json={
            "event_id": "fc-123",
            "event_type": "flashcard_reviewed",
            "document_id": "doc-1",
            "data": {"card_id": "card-1", "difficulty": "Hard"},
        },
    )
    assert response.status_code == 204


def test_get_analytics(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/analytics?time_range=7d", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "quizzes_completed" in data
    assert "average_quiz_accuracy" in data
    assert "flashcards_reviewed" in data
