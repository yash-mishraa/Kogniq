from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from persistence.uow_factory import AbstractUnitOfWorkFactory

from application.exceptions import ApplicationError
from application.interfaces import AuthenticationServiceProtocol


@dataclass(frozen=True)
class ChatSessionDto:
    id: str
    title: str | None
    document_id: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ChatMessageDto:
    id: str
    role: str
    content: str
    tool_events: list[str] | None
    created_at: datetime


class ListChatSessionsUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._uow_factory = uow_factory

    async def execute(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[ChatSessionDto]:
        with self._uow_factory.create() as uow:
            sessions = uow.chat.list_sessions_by_user(user_id, limit, offset)
            return [
                ChatSessionDto(
                    id=s.id,
                    title=s.title,
                    document_id=s.document_id,
                    created_at=s.created_at,
                    updated_at=s.updated_at,
                )
                for s in sessions
            ]


class GetChatHistoryUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._uow_factory = uow_factory

    async def execute(
        self, user_id: str, session_id: str, limit: int = 50
    ) -> Sequence[ChatMessageDto]:
        with self._uow_factory.create() as uow:
            session = uow.chat.get_session(session_id, user_id)
            if not session:
                raise ApplicationError("Session not found or permission denied.")

            messages = uow.chat.get_messages_for_session(session_id, user_id, limit)
            import json

            result = []
            for m in messages:
                events = None
                if m.tool_events:
                    try:
                        events = json.loads(m.tool_events)
                    except Exception:
                        pass

                result.append(
                    ChatMessageDto(
                        id=m.id,
                        role=m.role,
                        content=m.content,
                        tool_events=events,
                        created_at=m.created_at,
                    )
                )
            return result
