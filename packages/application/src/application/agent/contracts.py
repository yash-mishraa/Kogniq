from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TutorChatMessage:
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class TutorChatRequest:
    user_id: str
    messages: list[TutorChatMessage]
    document_id: str | None = None
    session_id: str | None = None


@dataclass(frozen=True)
class TutorChatResponse:
    content: str
    tool_events: list[str]
    session_id: str | None = None
