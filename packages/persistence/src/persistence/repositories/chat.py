import abc
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChatSessionEntity:
    id: str
    user_id: str
    document_id: str | None
    title: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ChatMessageEntity:
    id: str
    session_id: str
    role: str
    content: str
    tool_events: str | None
    created_at: datetime


class AbstractChatRepository(abc.ABC):
    @abc.abstractmethod
    def create_session(self, session: ChatSessionEntity) -> None:
        pass

    @abc.abstractmethod
    def get_session(self, session_id: str, user_id: str) -> ChatSessionEntity | None:
        pass

    @abc.abstractmethod
    def list_sessions_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0, document_id: str | None = None
    ) -> Sequence[ChatSessionEntity]:
        pass

    @abc.abstractmethod
    def add_message(self, message: ChatMessageEntity) -> None:
        pass

    @abc.abstractmethod
    def get_messages_for_session(
        self, session_id: str, user_id: str, limit: int = 50
    ) -> Sequence[ChatMessageEntity]:
        pass
