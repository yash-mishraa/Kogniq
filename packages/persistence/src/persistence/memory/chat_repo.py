from collections.abc import Sequence

from persistence.repositories.chat import (
    AbstractChatRepository,
    ChatMessageEntity,
    ChatSessionEntity,
)


class MemoryChatRepository(AbstractChatRepository):
    def __init__(self) -> None:
        self._sessions: dict[str, ChatSessionEntity] = {}
        self._messages: list[ChatMessageEntity] = []

    def create_session(self, session: ChatSessionEntity) -> None:
        self._sessions[session.id] = session

    def get_session(self, session_id: str, user_id: str) -> ChatSessionEntity | None:
        session = self._sessions.get(session_id)
        if session and session.user_id == user_id:
            return session
        return None

    def list_sessions_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[ChatSessionEntity]:
        sessions = [s for s in self._sessions.values() if s.user_id == user_id]
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions[offset : offset + limit]

    def add_message(self, message: ChatMessageEntity) -> None:
        self._messages.append(message)
        session = self._sessions.get(message.session_id)
        if session:
            # Update updated_at
            new_session = ChatSessionEntity(
                id=session.id,
                user_id=session.user_id,
                document_id=session.document_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=message.created_at,
            )
            self._sessions[session.id] = new_session

    def get_messages_for_session(
        self, session_id: str, user_id: str, limit: int = 50
    ) -> Sequence[ChatMessageEntity]:
        if not self.get_session(session_id, user_id):
            return []

        # Messages are likely appended chronologically, so we reverse to get latest
        session_messages = [m for m in self._messages if m.session_id == session_id]
        session_messages.sort(key=lambda m: m.created_at, reverse=True)

        limited = session_messages[:limit]
        limited.reverse()  # return in chronological order
        return limited
