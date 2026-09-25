import logging
from typing import Annotated

from backend.dependencies import (
    get_chat_history_use_case,
    get_list_chat_sessions_use_case,
    get_tutor_chat_use_case,
)
from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, Field

from application.agent.contracts import TutorChatMessage, TutorChatRequest
from application.agent.history import GetChatHistoryUseCase, ListChatSessionsUseCase
from application.agent.tutor_chat import TutorChatUseCase
from application.exceptions import ApplicationError
from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.auth import CurrentUserDependency

logger = logging.getLogger(__name__)

agent_router = APIRouter(prefix="/agent", tags=["Agent"])

TutorChatUseCaseDependency = Annotated[TutorChatUseCase, Depends(get_tutor_chat_use_case)]
ListSessionsUseCaseDependency = Annotated[
    ListChatSessionsUseCase, Depends(get_list_chat_sessions_use_case)
]
GetHistoryUseCaseDependency = Annotated[GetChatHistoryUseCase, Depends(get_chat_history_use_case)]

_ALLOWED_ROLES = ("user", "assistant")


class ChatMessageDto(BaseModel):
    role: str
    content: str = Field(max_length=2000)


class TutorChatRequestDto(BaseModel):
    messages: list[ChatMessageDto] = Field(max_length=20)
    document_id: str | None = Field(default=None)
    session_id: str | None = None


class TutorChatResponseDto(BaseModel):
    content: str
    tool_events: list[str]
    session_id: str | None = None


class SessionDto(BaseModel):
    id: str
    title: str | None
    document_id: str | None
    created_at: str
    updated_at: str


class SessionMessageDto(BaseModel):
    id: str
    role: str
    content: str
    tool_events: list[str] | None
    created_at: str


@agent_router.post("/tutor/chat", response_model=TutorChatResponseDto)
async def tutor_chat(
    request: TutorChatRequestDto,
    current_user: CurrentUserDependency,
    use_case: TutorChatUseCaseDependency,
) -> TutorChatResponseDto:
    """Run a bounded, read-only tutoring turn for the authenticated user."""
    for message in request.messages:
        if message.role not in _ALLOWED_ROLES:
            raise APIError(
                status_code=400,
                code="invalid_message_role",
                message="Messages must use the 'user' or 'assistant' role.",
            )

    chat_request = TutorChatRequest(
        user_id=current_user.user_id,
        document_id=request.document_id,
        messages=[
            TutorChatMessage(role=m.role, content=m.content)  # type: ignore[arg-type]
            for m in request.messages
        ],
        session_id=request.session_id,
    )

    try:
        response = await use_case.execute(chat_request)
    except ApplicationError as e:
        if "Permission denied" in str(e) or "Session not found" in str(e):
            raise APIError(status_code=403, code="permission_denied", message=str(e)) from e
        raise APIError(status_code=400, code="invalid_request", message=str(e)) from e
    except Exception:
        logger.exception("Tutor chat request failed unexpectedly")
        raise APIError(
            status_code=500,
            code="internal_error",
            message="The tutor could not complete this request.",
        ) from None

    return TutorChatResponseDto(
        content=response.content,
        tool_events=response.tool_events,
        session_id=response.session_id,
    )


@agent_router.get("/tutor/sessions", response_model=list[SessionDto])
async def list_chat_sessions(
    current_user: CurrentUserDependency,
    use_case: ListSessionsUseCaseDependency,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    document_id: str | None = Query(None),
) -> list[SessionDto]:
    """List chat sessions owned by the authenticated user."""
    try:
        sessions = await use_case.execute(user_id=current_user.user_id, limit=limit, offset=offset, document_id=document_id)
        return [
            SessionDto(
                id=s.id,
                title=s.title,
                document_id=s.document_id,
                created_at=s.created_at.isoformat(),
                updated_at=s.updated_at.isoformat(),
            )
            for s in sessions
        ]
    except ApplicationError as e:
        raise APIError(status_code=400, code="invalid_request", message=str(e)) from e


@agent_router.get("/tutor/sessions/{session_id}/messages", response_model=list[SessionMessageDto])
async def get_chat_history(
    current_user: CurrentUserDependency,
    use_case: GetHistoryUseCaseDependency,
    session_id: str = Path(...),
    limit: int = Query(50, ge=1, le=100),
) -> list[SessionMessageDto]:
    """Retrieve messages for an authenticated user's session."""
    try:
        messages = await use_case.execute(
            user_id=current_user.user_id, session_id=session_id, limit=limit
        )
        return [
            SessionMessageDto(
                id=m.id,
                role=m.role,
                content=m.content,
                tool_events=m.tool_events,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ]
    except ApplicationError as e:
        if "Session not found" in str(e):
            raise APIError(status_code=404, code="not_found", message=str(e)) from e
        raise APIError(status_code=400, code="invalid_request", message=str(e)) from e
