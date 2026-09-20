import typing
from datetime import datetime

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
        
    conn = sqlite3.connect(db_path, isolation_level=None)
    init_db(conn)
    
    factory = DefaultUnitOfWorkFactory(provider="sqlite", sqlite_path=db_path)
    yield factory
    
    conn.close()
    import os
    os.unlink(db_path)

@pytest.fixture
def uow_factory(sqlite_uow_factory: AbstractUnitOfWorkFactory) -> AbstractUnitOfWorkFactory:
    return sqlite_uow_factory

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

    return TestClient(app)

@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer session-123"}

from domain.student.entities import KnowledgeState


@pytest.fixture
def test_knowledge_state() -> KnowledgeState:
    return KnowledgeState(
        id="state-1",
        user_id="user-123",
        resource_id="doc-123",
        mastery_score=0.85,
        created_at=datetime(2026, 9, 20),
        updated_at=datetime(2026, 9, 20),
        last_reviewed_at=datetime(2026, 9, 20),
        next_review_due=datetime(2026, 9, 25),
    )


def test_knowledge_state_validation() -> None:
    # Valid
    KnowledgeState(
        id="test", user_id="u", resource_id="r", mastery_score=0.5,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    
    # Invalid
    with pytest.raises(ValueError):
        KnowledgeState(
            id="test", user_id="u", resource_id="r", mastery_score=1.5,
            created_at=datetime.now(), updated_at=datetime.now()
        )
    with pytest.raises(ValueError):
        KnowledgeState(
            id="test", user_id="u", resource_id="r", mastery_score=-0.1,
            created_at=datetime.now(), updated_at=datetime.now()
        )


@pytest.mark.asyncio
async def test_student_router_get_not_found(client: "TestClient", auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/student/knowledge-states/not-exist", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["message"] == "Knowledge state not found"


@pytest.mark.asyncio
async def test_student_router_list_empty(client: "TestClient", auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/student/knowledge-states", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == {"states": []}


@pytest.mark.asyncio
async def test_student_repository_upsert(
    uow_factory: AbstractUnitOfWorkFactory, test_knowledge_state: KnowledgeState
) -> None:
    # SQLite isolation test
    with uow_factory.create() as uow:
        res1 = await uow.knowledge_states.save(test_knowledge_state)
        # Should be a new record initially
        assert res1.id == "state-1"
        
        # Test retrieval
        state = await uow.knowledge_states.get("user-123", "doc-123")
        assert state is not None
        assert state.mastery_score == 0.85

        # Test upsert with updated values
        updated = KnowledgeState(
            id="state-1",
            user_id="user-123",
            resource_id="doc-123",
            mastery_score=0.95,
            created_at=test_knowledge_state.created_at,
            updated_at=datetime(2026, 9, 21),
            last_reviewed_at=datetime(2026, 9, 21),
            next_review_due=datetime(2026, 9, 30),
        )
        res2 = await uow.knowledge_states.save(updated)
        
        state2 = await uow.knowledge_states.get("user-123", "doc-123")
        assert state2.mastery_score == 0.95
        assert state2.updated_at == datetime(2026, 9, 21)


@pytest.mark.asyncio
async def test_student_router_ownership_isolation(
    client: TestClient, 
    auth_headers: dict[str, str], 
    uow_factory: AbstractUnitOfWorkFactory, 
    test_knowledge_state: KnowledgeState
) -> None:
    # Save a state belonging to 'user-123'
    # Wait, the auth_headers correspond to a specific user. In Kogniq tests, auth_headers defaults to "user_id": "test-user-id" or similar.
    # Let's seed a state for "another-user"
    other_state = KnowledgeState(
        id="state-other",
        user_id="another-user",
        resource_id="doc-shared",
        mastery_score=1.0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    with uow_factory.create() as uow:
        await uow.knowledge_states.save(other_state)

    # The current test-user should NOT be able to see another-user's state
    resp = client.get("/api/v1/student/knowledge-states/doc-shared", headers=auth_headers)
    assert resp.status_code == 404
