import sqlite3
from datetime import UTC, datetime

import pytest
from persistence.repositories.chat import ChatMessageEntity, ChatSessionEntity
from persistence.sqlite.chat_repository import SQLiteChatRepository


@pytest.fixture
def sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    from persistence.sqlite.schema import init_db

    init_db(conn)
    return conn


@pytest.fixture
def chat_repo(sqlite_conn: sqlite3.Connection) -> SQLiteChatRepository:
    return SQLiteChatRepository(sqlite_conn)


def test_session_creation_and_retrieval(chat_repo: SQLiteChatRepository) -> None:
    now = datetime.now(UTC)
    session = ChatSessionEntity(
        id="sess-1",
        user_id="user-1",
        document_id="doc-1",
        title="Test Session",
        created_at=now,
        updated_at=now,
    )
    chat_repo.create_session(session)

    retrieved = chat_repo.get_session("sess-1", "user-1")
    assert retrieved is not None
    assert retrieved.id == "sess-1"
    assert retrieved.title == "Test Session"

    # User isolation
    assert chat_repo.get_session("sess-1", "user-2") is None


def test_message_persistence_and_ordering(chat_repo: SQLiteChatRepository) -> None:
    now = datetime.now(UTC)
    session = ChatSessionEntity(
        id="sess-2",
        user_id="user-1",
        document_id=None,
        title=None,
        created_at=now,
        updated_at=now,
    )
    chat_repo.create_session(session)

    msg1 = ChatMessageEntity(
        id="msg-1",
        session_id="sess-2",
        role="user",
        content="Hi",
        tool_events=None,
        created_at=now,
    )
    chat_repo.add_message(msg1)

    messages = chat_repo.get_messages_for_session("sess-2", "user-1", limit=10)
    assert len(messages) == 1
    assert messages[0].content == "Hi"

    # User isolation
    assert len(chat_repo.get_messages_for_session("sess-2", "user-2")) == 0
