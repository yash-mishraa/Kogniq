# ruff: noqa: E501
import typing
from typing import Any

import pytest
from fastapi.testclient import TestClient
from persistence.uow_factory import AbstractUnitOfWorkFactory

from apps.api.app.main import create_app


@pytest.fixture
def sqlite_uow_factory() -> typing.Generator[AbstractUnitOfWorkFactory, None, None]:
    import sqlite3
    import tempfile

    from backend.dependencies import DefaultUnitOfWorkFactory
    from persistence.sqlite.schema import init_db
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
        
    conn = sqlite3.connect(db_path)
    init_db(conn)
    conn.close()
    
    factory = DefaultUnitOfWorkFactory(provider="sqlite", sqlite_path=db_path)
    yield factory
    
    import contextlib
    from pathlib import Path
    with contextlib.suppress(Exception):
        Path(db_path).unlink()


@pytest.fixture
def client(sqlite_uow_factory: AbstractUnitOfWorkFactory) -> TestClient:
    app = create_app()

    class MockSession:
        def __init__(self, user_id: str = "user-123") -> None:
            self.user_id = user_id

    class MockAuthService:
        async def validate_session(self, token: str) -> MockSession | None:
            if token == "session-123":
                return MockSession("user-123")
            if token == "session-456":
                return MockSession("user-456")
            return None

    from backend.dependencies import get_authentication_service, get_uow_factory

    app.dependency_overrides[get_authentication_service] = lambda: MockAuthService()
    app.dependency_overrides[get_uow_factory] = lambda: sqlite_uow_factory

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
        with sqlite_uow_factory.create() as uow:
            await uow.documents.save(doc)

    asyncio.run(seed())

    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer session-123"}


def test_record_event_quiz(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "quiz-123",
                "event_type": "quiz_completed",
                "resource_id": "doc-1",
                "data": {"score": 3, "total_questions": 4},
                "idempotency_key": "quiz-idem",
            }]
        },
    )
    assert response.status_code == 204


def test_record_event_flashcard(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "fc-123",
                "event_type": "flashcard_reviewed",
                "resource_id": "doc-1",
                "data": {"card_id": "c1", "difficulty": "easy"},
                "idempotency_key": "fc-idem",
            }]
        },
    )
    assert response.status_code == 204

def test_record_event_study_session(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "study-123",
                "event_type": "study_session_completed",
                "resource_id": "doc-1",
                "data": {"completed_at": "2026-09-19T10:00:00Z"},
                "idempotency_key": "study-idem",
            }]
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


def test_record_events_batch(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers={"Authorization": "Bearer session-123"},
        json={
            "events": [
                {
                    "event_id": "test-batch-1",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-1",
                    "data": {},
                    "idempotency_key": "view_1",
                }
            ]
        },
    )
    assert response.status_code == 204


def test_get_resource_progress(client: TestClient) -> None:
    headers = {"Authorization": "Bearer session-123"}
    client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "ev-prog",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-1",
                    "data": {},
                    "idempotency_key": "idem-prog",
                }
            ]
        },
    )

    response = client.get(
        "/api/v1/analytics/progress/doc-1",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resource_opened"] is True
    assert "viewed_chunks" in data


def test_analytics_comprehensive(client: TestClient) -> None:
    headers = {"Authorization": "Bearer session-123"}

    # Missing resource
    resp = client.get("/api/v1/analytics/progress/nonexistent", headers=headers)
    assert resp.status_code == 404

    # 1. valid resource_viewed
    # 1. valid resource_viewed
    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "cross-1",
                    "resource_id": "doc-other-user",
                    "event_type": "chunk_viewed",
                    "data": {"section_id": "s1", "chunk_id": "c1"},
                    "idempotency_key": "cross-1"
                },
                {
                    "event_id": "cross-2",
                    "resource_id": "doc-other-user",
                    "event_type": "quiz_completed",
                    "data": {"score": 5, "total_questions": 10},
                    "idempotency_key": "cross-2"
                },
                {
                    "event_id": "cross-3",
                    "resource_id": "doc-other-user",
                    "event_type": "flashcard_reviewed",
                    "data": {"card_id": "c1", "difficulty": "hard"},
                    "idempotency_key": "cross-3"
                },
                {
                    "event_id": "cross-4",
                    "resource_id": "doc-other-user",
                    "event_type": "study_session_completed",
                    "data": {"completed_at": "2026-09-19T00:00:00Z"},
                    "idempotency_key": "cross-4"
                }
            ]
        },
    )
    assert resp.status_code == 404

    # Duplicate idempotency
    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "ev-2",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-1",
                    "data": {},
                    "idempotency_key": "idem-1",
                }
            ]
        },
    )
    assert resp.status_code == 204

    # Duplicate primary key (same event_id)
    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "ev-1",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-1",
                    "data": {},
                    "idempotency_key": "idem-2",
                }
            ]
        },
    )
    assert resp.status_code == 204

    # valid chunk_viewed
    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "ev-3",
                    "event_type": "chunk_viewed",
                    "resource_id": "doc-1",
                    "section_id": "sec-1",
                    "chunk_id": "chunk-1",
                    "data": {},
                    "idempotency_key": "idem-3",
                }
            ]
        },
    )
    # This might return 400 because section and chunk do not exist!
    assert resp.status_code == 400


def test_batch_atomic_rollback(client: TestClient, sqlite_uow_factory: AbstractUnitOfWorkFactory) -> None:
    headers = {"Authorization": "Bearer session-123"}
    import asyncio
    from datetime import UTC, datetime

    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage

    uow_factory = sqlite_uow_factory

    async def seed() -> None:
        doc = NormalizedDocument(
            id="doc-atomic",
            title="test",
            source="test",
            checksum="2",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-123",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc)

    asyncio.run(seed())

    # Check initial state
    with uow_factory.create() as uow:
        initial_events = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE id IN ('atomic-valid', 'atomic-invalid')"
        ).fetchone()[0]
        assert initial_events == 0

    # Submit batch with one valid and one invalid event
    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "atomic-valid",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-atomic",
                    "data": {},
                    "idempotency_key": "atomic-1",
                },
                {
                    "event_id": "atomic-invalid",
                    "event_type": "chunk_viewed",
                    "resource_id": "doc-atomic",
                    "section_id": "invalid",
                    "chunk_id": "invalid",
                    "data": {},
                    "idempotency_key": "atomic-2",
                },
            ]
        },
    )
    assert resp.status_code == 400

    # Verify complete rollback (the valid resource_viewed event was dropped)
    resp = client.get("/api/v1/analytics/progress/doc-atomic", headers=headers)
    assert resp.json().get("resource_opened") is False

    with uow_factory.create() as uow:
        events = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE id IN ('atomic-valid', 'atomic-invalid')"
        ).fetchone()[0]
        assert events == 0  # Prove zero events inserted


def test_idempotency_normalization_and_nulls(client: TestClient, sqlite_uow_factory: AbstractUnitOfWorkFactory) -> None:
    headers = {"Authorization": "Bearer session-123"}
    import asyncio
    from datetime import UTC, datetime

    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage

    uow_factory = sqlite_uow_factory

    async def seed() -> None:
        doc = NormalizedDocument(
            id="doc-idem",
            title="test",
            source="test",
            checksum="3",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-123",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc)

    asyncio.run(seed())

    # 1. Empty string / whitespace becomes NULL.
    # SQLite UNIQUE ignores NULL, allowing duplicate non-deduped events!
    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "idem-null-1",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-idem",
                    "data": {},
                    "idempotency_key": "",
                },
                {
                    "event_id": "idem-null-2",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-idem",
                    "data": {},
                    "idempotency_key": "   ",
                },
            ]
        },
    )
    assert resp.status_code == 204

    # 2. Duplicate client keys correctly deduped
    client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "idem-norm-1",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-idem",
                    "data": {},
                    "idempotency_key": "same-key",
                },
                {
                    "event_id": "idem-norm-2",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-idem",
                    "data": {},
                    "idempotency_key": "same-key",
                },
            ]
        },
    )

    # 3. Client trying to spoof another user's prefix
    client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "idem-spoof",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-idem",
                    "data": {},
                    "idempotency_key": "otheruser::key",
                }
            ]
        },
    )

    with uow_factory.create() as uow:
        # Verify nulls
        null_count = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE id IN ('idem-null-1', 'idem-null-2') "
            "AND idempotency_key IS NULL"
        ).fetchone()[0]
        assert null_count == 2

        # Verify normalization and dedup (only one should exist for same-key)
        norm_count = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE idempotency_key = 'user-123::same-key'"
        ).fetchone()[0]
        assert norm_count == 1

        # Verify spoof prevention (it prepends the real user_id unconditionally)
        spoof_count = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity "
            "WHERE idempotency_key = 'user-123::otheruser::key'"
        ).fetchone()[0]
        assert spoof_count == 1

def test_transactional_rollback_on_mid_batch_failure(client: TestClient, sqlite_uow_factory: AbstractUnitOfWorkFactory) -> None:
    headers = {"Authorization": "Bearer session-123"}
    import asyncio
    from datetime import UTC, datetime

    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage

    uow_factory = sqlite_uow_factory

    async def seed() -> None:
        doc = NormalizedDocument(
            id="doc-rollback",
            title="test",
            source="test",
            checksum="3",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-123",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc)
            # Add a native SQLite trigger to fail exactly when a specific event ID is inserted
            # This simulates a native mid-batch failure inside executemany, without any Python mocks.
            uow.analytics._conn.execute(  # type: ignore
                """
                CREATE TRIGGER fail_mid_batch BEFORE INSERT ON learner_activity
                FOR EACH ROW
                WHEN NEW.id = 'trigger-fail'
                BEGIN
                    SELECT RAISE(FAIL, 'Simulated mid-batch failure');
                END;
                """
            )

    asyncio.run(seed())

    # Send a batch: valid event, failing event, valid event
    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "valid-1",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-rollback",
                    "data": {},
                    "idempotency_key": "valid-1",
                },
                {
                    "event_id": "trigger-fail",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-rollback",
                    "data": {},
                    "idempotency_key": "trigger-fail",
                },
                {
                    "event_id": "valid-2",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-rollback",
                    "data": {},
                    "idempotency_key": "valid-2",
                }
            ]
        },
    )
    # Fastapi will catch the sqlite3.IntegrityError or OperationalError as a 500
    assert resp.status_code == 500, f"Expected 500 but got {resp.status_code} - {resp.text}"

    # Because of atomicity, neither valid-1 nor valid-2 should be in the database
    with uow_factory.create() as uow:
        count = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE id IN ('valid-1', 'valid-2')"
        ).fetchone()[0]
        assert count == 0

def test_cross_user_isolation(client: TestClient, sqlite_uow_factory: AbstractUnitOfWorkFactory) -> None:
    headers = {"Authorization": "Bearer session-123"}
    import asyncio
    from datetime import UTC, datetime

    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    uow_factory = sqlite_uow_factory

    async def seed() -> None:
        doc = NormalizedDocument(
            id="doc-other-user",
            title="test",
            source="test",
            checksum="4",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-999",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc)

    asyncio.run(seed())

    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "ev-spoof",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-other-user",
                    "data": {},
                    "idempotency_key": "spoof-key",
                }
            ]
        },
    )
    assert resp.status_code == 403

    with uow_factory.create() as uow:
        count = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE id = 'ev-spoof'"
        ).fetchone()[0]
        assert count == 0

def test_comprehensive_cross_user_isolation(client: TestClient, sqlite_uow_factory: AbstractUnitOfWorkFactory) -> None:
    headers = {"Authorization": "Bearer session-123"}
    import asyncio
    from datetime import UTC, datetime

    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    uow_factory = sqlite_uow_factory

    async def seed() -> None:
        doc = NormalizedDocument(
            id="doc-other-user",
            title="test",
            source="test",
            checksum="4",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-999",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc)

    asyncio.run(seed())

    # Submit separate batches for each event type to prove they ALL validate ownership independently
    events_to_test = [
        {
            "event_id": "idor-1",
            "event_type": "resource_viewed",
            "resource_id": "doc-other-user",
            "data": {},
            "idempotency_key": "idor-key-1",
        },
        {
            "event_id": "idor-2",
            "event_type": "chunk_viewed",
            "resource_id": "doc-other-user",
            "data": {"section_id": "sec-1", "chunk_id": "chk-1"},
            "idempotency_key": "idor-key-2",
        },
        {
            "event_id": "idor-3",
            "event_type": "quiz_completed",
            "resource_id": "doc-other-user",
            "data": {"score": 5, "total_questions": 10},
            "idempotency_key": "idor-key-3",
        },
        {
            "event_id": "idor-4",
            "event_type": "flashcard_reviewed",
            "resource_id": "doc-other-user",
            "data": {"card_id": "c1", "difficulty": "hard"},
            "idempotency_key": "idor-key-4",
        },
        {
            "event_id": "idor-5",
            "event_type": "study_session_completed",
            "resource_id": "doc-other-user",
            "data": {"completed_at": "2026-09-19T00:00:00Z"},
            "idempotency_key": "idor-key-5",
        }
    ]

    for ev in events_to_test:
        resp = client.post(
            "/api/v1/analytics/events/batch",
            headers=headers,
            json={"events": [ev]},
        )
        assert resp.status_code == 403, f"Expected 403 for {ev['event_type']}"

    # Mixed batch: one valid document, one invalid document
    async def seed_valid() -> None:
        doc = NormalizedDocument(
            id="doc-valid-user",
            title="test",
            source="test",
            checksum="4",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-123",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc)
    asyncio.run(seed_valid())

    resp = client.post(
        "/api/v1/analytics/events/batch",
        headers=headers,
        json={
            "events": [
                {
                    "event_id": "idor-valid",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-valid-user",
                    "data": {},
                    "idempotency_key": "idor-valid",
                },
                {
                    "event_id": "idor-invalid",
                    "event_type": "resource_viewed",
                    "resource_id": "doc-other-user",
                    "data": {},
                    "idempotency_key": "idor-invalid",
                }
            ]
        },
    )
    # The entire batch should be rejected because one resource is unauthorized
    assert resp.status_code == 403
    
    with uow_factory.create() as uow:
        count = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE id = 'idor-valid'"
        ).fetchone()[0]
        assert count == 0


def test_comprehensive_idempotency(client: TestClient, sqlite_uow_factory: AbstractUnitOfWorkFactory) -> None:
    headers_1 = {"Authorization": "Bearer session-123"}
    headers_2 = {"Authorization": "Bearer session-456"}
    import asyncio
    from datetime import UTC, datetime

    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage
    uow_factory = sqlite_uow_factory

    async def seed() -> None:
        doc1 = NormalizedDocument(
            id="doc-idem-1",
            title="test",
            source="test",
            checksum="4",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-123",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        doc2 = NormalizedDocument(
            id="doc-idem-2",
            title="test",
            source="test",
            checksum="4",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-456",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with uow_factory.create() as uow:
            await uow.documents.save(doc1)
            await uow.documents.save(doc2)

    asyncio.run(seed())

    # 1. Same user + same key + same payload
    payload_1 = {
        "event_id": "idem-1",
        "event_type": "resource_viewed",
        "resource_id": "doc-idem-1",
        "data": {},
        "idempotency_key": "idem-key",
    }
    resp1 = client.post("/api/v1/analytics/events/batch", headers=headers_1, json={"events": [payload_1]})
    resp2 = client.post("/api/v1/analytics/events/batch", headers=headers_1, json={"events": [payload_1]})
    assert resp1.status_code == 204
    assert resp2.status_code == 204

    # 2. Same user + same key + different payload
    payload_2 = {
        "event_id": "idem-2",
        "event_type": "quiz_completed",
        "resource_id": "doc-idem-1",
        "data": {"score": 10, "total_questions": 10},
        "idempotency_key": "idem-key",
    }
    resp3 = client.post("/api/v1/analytics/events/batch", headers=headers_1, json={"events": [payload_2]})
    assert resp3.status_code == 204

    # 3. Different user + same key
    payload_3 = {
        "event_id": "idem-3",
        "event_type": "resource_viewed",
        "resource_id": "doc-idem-2",
        "data": {},
        "idempotency_key": "idem-key",
    }
    resp4 = client.post("/api/v1/analytics/events/batch", headers=headers_2, json={"events": [payload_3]})
    assert resp4.status_code == 204

    # 4. Duplicate events within ONE batch
    payload_4a = {
        "event_id": "idem-4",
        "event_type": "resource_viewed",
        "resource_id": "doc-idem-1",
        "data": {},
        "idempotency_key": "idem-batch-dup",
    }
    payload_4b = {
        "event_id": "idem-5",
        "event_type": "resource_viewed",
        "resource_id": "doc-idem-1",
        "data": {},
        "idempotency_key": "idem-batch-dup",
    }
    resp5 = client.post("/api/v1/analytics/events/batch", headers=headers_1, json={"events": [payload_4a, payload_4b]})
    assert resp5.status_code == 204

    # Verify actual row counts
    with uow_factory.create() as uow:
        # Only one row for user-123 idem-key
        count_user1 = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE user_id = 'user-123' AND idempotency_key = 'user-123::idem-key'"
        ).fetchone()[0]
        assert count_user1 == 1

        # One row for user-456 idem-key
        count_user2 = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE user_id = 'user-456' AND idempotency_key = 'user-456::idem-key'"
        ).fetchone()[0]
        assert count_user2 == 1

        # One row for user-123 idem-batch-dup
        count_batch = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE user_id = 'user-123' AND idempotency_key = 'user-123::idem-batch-dup'"
        ).fetchone()[0]
        assert count_batch == 1
def test_record_events_batch_invalid_event_type(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "inv-123",
                "event_type": "unknown_event",
                "resource_id": "doc-1",
                "data": {},
            }]
        },
    )
    assert response.status_code == 400
    assert "Unknown event" in response.json().get("error", {}).get("message", response.text)


def test_record_events_batch_missing_fields(client: TestClient, auth_headers: dict[str, str]) -> None:
    # Quiz missing score
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "quiz-missing",
                "event_type": "quiz_completed",
                "resource_id": "doc-1",
                "data": {"total_questions": 4},
            }]
        },
    )
    assert response.status_code == 400
    assert "quiz_completed requires score" in response.json().get("error", {}).get("message", response.text)

    # Flashcard missing difficulty
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "fc-missing",
                "event_type": "flashcard_reviewed",
                "resource_id": "doc-1",
                "data": {"card_id": "c1"},
            }]
        },
    )
    assert response.status_code == 400
    assert "flashcard_reviewed missing card" in response.json().get("error", {}).get("message", response.text)

def test_record_events_batch_malformed_fields(client: TestClient, auth_headers: dict[str, str]) -> None:
    # Quiz with boolean score
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "q1",
                "event_type": "quiz_completed",
                "resource_id": "doc-1",
                "data": {"score": True, "total_questions": 5},
            }]
        },
    )
    assert response.status_code == 400
    assert "quiz numeric score required" in response.json().get("error", {}).get("message", "")

    # Quiz with score > total_questions
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "q1",
                "event_type": "quiz_completed",
                "resource_id": "doc-1",
                "data": {"score": 6, "total_questions": 5},
            }]
        },
    )
    assert response.status_code == 400
    assert "score cannot exceed total_questions" in response.json().get("error", {}).get("message", "")
    
    
    # Study session with invalid ISO date
    response = client.post(
        "/api/v1/analytics/events/batch",
        headers=auth_headers,
        json={
            "events": [{
                "event_id": "s1",
                "event_type": "study_session_completed",
                "resource_id": "doc-1",
                "data": {"completed_at": "not-a-date"},
            }]
        },
    )
    assert response.status_code == 400
    assert "completed_at must be ISO-8601" in response.json().get("error", {}).get("message", "")

def test_record_event_study_session_idempotency(client: TestClient, sqlite_uow_factory: AbstractUnitOfWorkFactory) -> None:
    headers = {"Authorization": "Bearer session-123"}
    import asyncio
    from datetime import UTC, datetime

    from content.normalized.document import NormalizedDocument
    from content.normalized.page import NormalizedPage

    async def seed() -> None:
        doc = NormalizedDocument(
            id="doc-study-idem",
            title="test",
            source="test",
            checksum="study",
            version="1",
            created_at=datetime.now(UTC),
            user_id="user-123",
            pages=(NormalizedPage(page_number=1, blocks=()),),
        )
        with sqlite_uow_factory.create() as uow:
            await uow.documents.save(doc)

    asyncio.run(seed())

    # Double click finish
    for _ in range(2):
        response = client.post(
            "/api/v1/analytics/events/batch",
            headers=headers,
            json={
                "events": [{
                    "event_id": "study-dup-123",
                    "event_type": "study_session_completed",
                    "resource_id": "doc-study-idem",
                    "data": {"completed_at": "2026-09-19T10:00:00Z"},
                    "idempotency_key": "study-session-req-1",
                }]
            },
        )
        assert response.status_code == 204

    # Verify only one event was saved
    with sqlite_uow_factory.create() as uow:
        count = uow.analytics._conn.execute(  # type: ignore
            "SELECT count(*) FROM learner_activity WHERE event_type = 'study_session_completed' AND document_id = 'doc-study-idem'"
        ).fetchone()[0]
        assert count == 1

def test_analytics_payload_exhaustive_validation(client: TestClient, auth_headers: dict[str, str]) -> None:
    
    def assert_invalid(event_type: str, data: dict[str, Any], expected_msg_fragment: str, top_level: dict[str, Any] | None = None) -> None:
        if top_level is None:
            top_level = {}
        payload = {
            "event_id": "test-id",
            "event_type": event_type,
            "resource_id": "doc-1",
            "idempotency_key": "test-id",
            "data": data,
        }
        payload.update(top_level)
        resp = client.post(
            "/api/v1/analytics/events/batch",
            headers=auth_headers,
            json={"events": [payload]}
        )
        assert resp.status_code in (400, 422), f"Expected 400/422 for {event_type} {data}, got {resp.status_code} - {resp.text}"
        assert expected_msg_fragment.lower() in resp.text.lower(), f"Expected {expected_msg_fragment} in {resp.text}"

    # chunk_viewed validation
    assert_invalid("chunk_viewed", {}, "missing ids", top_level={})
    assert_invalid("chunk_viewed", {}, "missing ids", top_level={"section_id": None, "chunk_id": "c1"})
    assert_invalid("chunk_viewed", {}, "missing ids", top_level={"section_id": "s1", "chunk_id": None})
    assert_invalid("chunk_viewed", {}, "string", top_level={"section_id": 123, "chunk_id": 123})

    # quiz_completed validation
    assert_invalid("quiz_completed", {}, "quiz_completed requires score")
    assert_invalid("quiz_completed", {"score": 5}, "quiz_completed requires score")
    assert_invalid("quiz_completed", {"score": None, "total_questions": 5}, "quiz numeric score required")
    assert_invalid("quiz_completed", {"score": -1, "total_questions": 5}, "score cannot be negative")
    assert_invalid("quiz_completed", {"score": 5, "total_questions": -1}, "positive int total_questions required")
    assert_invalid("quiz_completed", {"score": 6, "total_questions": 5}, "score cannot exceed total_questions")

    # flashcard_reviewed validation
    assert_invalid("flashcard_reviewed", {}, "missing card")
    assert_invalid("flashcard_reviewed", {"card_id": "c1"}, "missing card")
    assert_invalid("flashcard_reviewed", {"card_id": None, "difficulty": "easy"}, "card_id invalid")
    assert_invalid("flashcard_reviewed", {"card_id": "c1", "difficulty": None}, "invalid difficulty")
    assert_invalid("flashcard_reviewed", {"card_id": "c1", "difficulty": "invalid_diff"}, "invalid difficulty")

    # study_session_completed validation
    assert_invalid("study_session_completed", {}, "missing completed_at")
    assert_invalid("study_session_completed", {"completed_at": None}, "completed_at invalid")
    assert_invalid("study_session_completed", {"completed_at": "not-a-timestamp"}, "must be iso-8601")
# ruff: noqa: E501
