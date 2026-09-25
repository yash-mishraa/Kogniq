import sqlite3
from collections.abc import Sequence
from datetime import datetime

from persistence.repositories.chat import (
    AbstractChatRepository,
    ChatMessageEntity,
    ChatSessionEntity,
)


class SQLiteChatRepository(AbstractChatRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create_session(self, session: ChatSessionEntity) -> None:
        self._conn.execute(
            """
            INSERT INTO chat_sessions (id, user_id, document_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session.id,
                session.user_id,
                session.document_id,
                session.title,
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
            ),
        )

    def get_session(self, session_id: str, user_id: str) -> ChatSessionEntity | None:
        row = self._conn.execute(
            "SELECT * FROM chat_sessions WHERE id = ? AND user_id = ?",
            (session_id, user_id),
        ).fetchone()
        if not row:
            return None
        return ChatSessionEntity(
            id=row["id"],
            user_id=row["user_id"],
            document_id=row["document_id"],
            title=row["title"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_sessions_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0, document_id: str | None = None
    ) -> Sequence[ChatSessionEntity]:
        if document_id is not None:
            if document_id == "global":
                query = "SELECT * FROM chat_sessions WHERE user_id = ? AND document_id IS NULL ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params: tuple[object, ...] = (user_id, limit, offset) 
            else:
                query = "SELECT * FROM chat_sessions WHERE user_id = ? AND document_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params = (user_id, document_id, limit, offset)
        else:
            query = "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params = (user_id, limit, offset) 
        
        rows = self._conn.execute(query, params).fetchall()
        return [
            ChatSessionEntity(
                id=row["id"],
                user_id=row["user_id"],
                document_id=row["document_id"],
                title=row["title"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def add_message(self, message: ChatMessageEntity) -> None:
        self._conn.execute(
            """
            INSERT INTO chat_messages (id, session_id, role, content, tool_events, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                message.id,
                message.session_id,
                message.role,
                message.content,
                message.tool_events,
                message.created_at.isoformat(),
            ),
        )
        self._conn.execute(
            "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
            (message.created_at.isoformat(), message.session_id),
        )

    def get_messages_for_session(
        self, session_id: str, user_id: str, limit: int = 50
    ) -> Sequence[ChatMessageEntity]:
        # Enforce user_id to ensure a user cannot query messages of someone else's session ID
        session = self.get_session(session_id, user_id)
        if not session:
            return []

        rows = self._conn.execute(
            """
            SELECT * FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()

        # We queried DESC for LIMIT, but we want them returned in chronological ASC order
        messages = [
            ChatMessageEntity(
                id=row["id"],
                session_id=row["session_id"],
                role=row["role"],
                content=row["content"],
                tool_events=row["tool_events"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]
        messages.reverse()
        return messages
