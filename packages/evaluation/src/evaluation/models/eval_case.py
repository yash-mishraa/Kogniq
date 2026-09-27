from typing import Any, Literal

from pydantic import BaseModel, Field


class EvalContext(BaseModel):
    user_id: str = "eval-user-1"
    document_id: str | None = None
    session_id: str = "eval-sess-1"
    retrieved_chunks: list[str] | None = None

class EvalInput(BaseModel):
    messages: list[dict[str, Any]] = Field(default_factory=list)

class ScriptedToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)

class ScriptedResponse(BaseModel):
    role: str = "assistant"
    content: str = ""
    tool_calls: list[ScriptedToolCall] = Field(default_factory=list)

class ScriptedProviderBehavior(BaseModel):
    responses: list[ScriptedResponse]

class EvalExpected(BaseModel):
    tool_calls_attempted: list[str] | None = None
    response_includes: str | None = None
    exception: str | None = None

class EvalCase(BaseModel):
    id: str
    category: Literal["functional", "safety", "authorization", "reliability", "security"]
    description: str
    context: EvalContext = Field(default_factory=EvalContext)
    input: EvalInput = Field(default_factory=EvalInput)
    scripted_provider: ScriptedProviderBehavior
    expected: EvalExpected
