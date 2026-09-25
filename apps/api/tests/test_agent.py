"""Tests for the agent tutor chat use case."""

from types import SimpleNamespace
from typing import Any

import pytest

from application.agent.contracts import TutorChatMessage, TutorChatRequest
from application.agent.tutor_chat import (
    MAX_ORCHESTRATION_ITERATIONS,
    TutorChatUseCase,
)
from application.exceptions import ApplicationError
from application.retrieval.commands import RetrievalCommand
from learning_content.providers.base import AgentMessage, ToolCall, ToolDefinition
from learning_content.providers.mock.provider import MockTextGenerationProvider


class FakeAuthorizationService:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed

    async def require_permission(self, user_id: str, permission_id: str) -> Any:
        del user_id, permission_id
        return SimpleNamespace(
            allowed=self.allowed,
            reason=None if self.allowed else "missing permission",
        )

    async def assign_role(self, user_id: str, role_id: str) -> None:
        del user_id, role_id
        raise AssertionError("not used by the tutor chat use case")


class FakeRetrieveUseCase:
    def __init__(self, contents: list[str] | None = None) -> None:
        self.commands: list[RetrievalCommand] = []
        self._contents = contents if contents is not None else [
            "Attention heads blend token representations.",
            "Multi-head attention runs several heads in parallel.",
        ]

    async def execute(self, command: RetrievalCommand) -> Any:
        self.commands.append(command)
        return SimpleNamespace(
            results=[SimpleNamespace(content=c) for c in self._contents]
        )


class FakeRecommendationsUseCase:
    def __init__(self, titles: list[str]) -> None:
        self._titles = titles

    async def execute_for_user(self, user_id: str, limit: int = 5) -> Any:
        del user_id
        return SimpleNamespace(
            recommendations=[
                SimpleNamespace(
                    resource_title=t,
                    resource_id=f"res-{i}",
                    action_type="review",
                    priority_score=0.9,
                    reason="due for review",
                )
                for i, t in enumerate(self._titles[:limit])
            ]
        )


class FakeKnowledgeStateUseCase:
    def __init__(self) -> None:
        self.last_resource_id: str | None = None

    async def execute_for_user(self, user_id: str, resource_id: str) -> Any:
        del user_id
        self.last_resource_id = resource_id
        if resource_id == "res-1":
            return SimpleNamespace(
                state=SimpleNamespace(
                    resource_id="res-1",
                    mastery_score=0.72,
                    last_reviewed_at=None,
                    next_review_due=None,
                )
            )
        return SimpleNamespace(state=None)


class ScriptedChatProvider:
    """Test double returning a fixed sequence of agent messages."""

    def __init__(self, responses: list[AgentMessage]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def generate_chat(
        self,
        messages: list[AgentMessage],
        tools: list[ToolDefinition] | None = None,
        system_instruction: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AgentMessage:
        self.calls.append({"messages": list(messages), "tools": tools})
        del system_instruction, temperature, max_tokens
        return self._responses.pop(0)


def build_request(messages: list[TutorChatMessage]) -> TutorChatRequest:
    return TutorChatRequest(user_id="user-1", document_id="doc-1", messages=messages)


def build_use_case(
    provider: Any,
    *,
    allowed: bool = True,
    retrieve: FakeRetrieveUseCase | None = None,
    recommendations: FakeRecommendationsUseCase | None = None,
    knowledge_state: FakeKnowledgeStateUseCase | None = None,
) -> TutorChatUseCase:
    from persistence.factory import MemoryRepositoryFactory
    from persistence.memory_uow import MemoryUnitOfWork
    
    from persistence.uow_factory import AbstractUnitOfWorkFactory
    class FakeUowFactory(AbstractUnitOfWorkFactory):
        def create(self) -> MemoryUnitOfWork:
            return MemoryUnitOfWork(MemoryRepositoryFactory())

    return TutorChatUseCase(
        auth_service=SimpleNamespace(),
        authorization_service=FakeAuthorizationService(allowed),
        retrieve_use_case=retrieve or FakeRetrieveUseCase(),  # type: ignore[arg-type]
        provider=provider,
        get_recommendations_use_case=recommendations or FakeRecommendationsUseCase([]),  # type: ignore[arg-type]
        get_knowledge_state_use_case=knowledge_state or FakeKnowledgeStateUseCase(),  # type: ignore[arg-type]
        uow_factory=FakeUowFactory(),
    )


def tool_message(name: str, arguments: dict[str, Any]) -> AgentMessage:
    return AgentMessage(
        role="assistant",
        content="",
        tool_calls=[ToolCall(id="call-1", name=name, arguments=arguments)],
    )


@pytest.mark.asyncio
async def test_permission_denied_raises_before_any_provider_call() -> None:
    provider = ScriptedChatProvider([])
    use_case = build_use_case(provider, allowed=False)

    with pytest.raises(ApplicationError):
        await use_case.execute(
            build_request([TutorChatMessage(role="user", content="hello")])
        )

    assert provider.calls == []


@pytest.mark.asyncio
async def test_conversation_length_is_bounded() -> None:
    use_case = build_use_case(ScriptedChatProvider([]))
    messages = [
        TutorChatMessage(role="user", content="m") for _ in range(21)
    ]

    with pytest.raises(ApplicationError):
        await use_case.execute(build_request(messages))


@pytest.mark.asyncio
async def test_individual_message_length_is_bounded() -> None:
    use_case = build_use_case(ScriptedChatProvider([]))

    with pytest.raises(ApplicationError):
        await use_case.execute(
            build_request([TutorChatMessage(role="user", content="x" * 2001)])
        )


@pytest.mark.asyncio
async def test_direct_answer_without_tool_calls() -> None:
    provider = ScriptedChatProvider(
        [AgentMessage(role="assistant", content="Attention is a mechanism.")]
    )
    use_case = build_use_case(provider)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="What is attention?")])
    )

    assert response.content == "Attention is a mechanism."
    assert response.tool_events == []
    assert len(provider.calls) == 1
    tool_names = {tool.name for tool in provider.calls[0]["tools"]}
    assert tool_names == {"semantic_search", "get_recommendations", "get_knowledge_state", "log_conversational_assessment", "generate_flashcard", "generate_quiz_question", "append_note", "query_knowledge_graph"}


@pytest.mark.asyncio
async def test_semantic_search_grounding_flow() -> None:
    retrieve = FakeRetrieveUseCase(["Attention heads blend token representations."])
    use_case = build_use_case(MockTextGenerationProvider(), retrieve=retrieve)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="What is attention?")])
    )

    assert response.content == (
        "Based on the document context: Chunk 1:\n"
        "Attention heads blend token representations."
    )
    assert response.tool_events == ["Searched document for: 'What is attention?'"]
    assert retrieve.commands[0].top_k == 3
    assert retrieve.commands[0].user_id == "user-1"
    assert retrieve.commands[0].document_id == "doc-1"


@pytest.mark.asyncio
async def test_get_recommendations_tool() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("get_recommendations", {"limit": 2}),
            AgentMessage(role="assistant", content="Here are your next steps."),
        ]
    )
    recommendations = FakeRecommendationsUseCase(["Attention Is All You Need"])
    use_case = build_use_case(provider, recommendations=recommendations)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="What should I study?")])
    )

    assert response.content == "Here are your next steps."
    assert response.tool_events == ["Retrieved learning recommendations."]
    assert "Attention Is All You Need" in provider.calls[1]["messages"][-1].content


@pytest.mark.asyncio
async def test_get_recommendations_rejects_out_of_range_limit() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("get_recommendations", {"limit": 9}),
            AgentMessage(role="assistant", content="No valid recommendations."),
        ]
    )
    use_case = build_use_case(provider)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="Recommend something")])
    )

    assert response.tool_events == [
        "Tool execution failed: limit must be between 1 and 5."
    ]
    assert response.content == "No valid recommendations."


@pytest.mark.asyncio
async def test_get_knowledge_state_tool() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("get_knowledge_state", {"resource_id": "res-1"}),
            AgentMessage(role="assistant", content="Mastery is 0.72."),
        ]
    )
    knowledge_state = FakeKnowledgeStateUseCase()
    use_case = build_use_case(provider, knowledge_state=knowledge_state)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="How am I doing?")])
    )

    assert response.content == "Mastery is 0.72."
    assert response.tool_events == ["Retrieved knowledge state for resource."]
    assert knowledge_state.last_resource_id == "res-1"
    tool_result = provider.calls[1]["messages"][-1].content
    assert "Resource ID: res-1" in tool_result
    assert "Mastery Score: 0.72" in tool_result


@pytest.mark.asyncio
async def test_get_knowledge_state_unknown_resource() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("get_knowledge_state", {"resource_id": "res-404"}),
            AgentMessage(role="assistant", content="No state found."),
        ]
    )
    use_case = build_use_case(provider)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="How am I doing?")])
    )

    assert response.tool_events == ["Retrieved knowledge state for resource."]
    tool_result = provider.calls[1]["messages"][-1].content
    assert tool_result == "State not found for resource 'res-404'."


@pytest.mark.asyncio
async def test_get_knowledge_state_requires_resource_id() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("get_knowledge_state", {}),
            AgentMessage(role="assistant", content="Please try again."),
        ]
    )
    use_case = build_use_case(provider)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="How am I doing?")])
    )

    assert response.tool_events == [
        "Tool execution failed: Missing or invalid resource_id."
    ]
    assert response.content == "Please try again."


@pytest.mark.asyncio
async def test_orchestration_loop_is_bounded() -> None:
    endless_tool_calls = [
        tool_message("semantic_search", {"query": f"q{i}"})
        for i in range(MAX_ORCHESTRATION_ITERATIONS)
    ]
    provider = ScriptedChatProvider(endless_tool_calls)
    use_case = build_use_case(provider)

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="Loop forever")])
    )

    assert response.content == "Too many steps taken. Please refine your question."
    assert response.tool_events[-1] == "Tool call limit reached."
    assert len(provider.calls) == MAX_ORCHESTRATION_ITERATIONS

@pytest.mark.asyncio
async def test_log_conversational_assessment_tool() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("log_conversational_assessment", {"score": 0.8, "rationale": "Good answer"}),
            AgentMessage(role="assistant", content="Mastery updated."),
        ]
    )
    knowledge_state = FakeKnowledgeStateUseCase()
    knowledge_state.last_resource_id = "doc-1"
    
    use_case = build_use_case(provider, knowledge_state=knowledge_state)
    
    from application.analytics.record_events_batch import RecordEventsBatchUseCase
    
    class FakeRecordEventsUseCase:
        def __init__(self, *args, **kwargs):
            self.recorded = []
        async def execute_for_user(self, user_id, request):
            self.recorded.append((user_id, request))
            
    fake_record = FakeRecordEventsUseCase()
    use_case._record_events_batch_use_case = fake_record

    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="Here is my answer.")])
    )

    assert response.content == "Mastery updated."
    assert "Logged conversational assessment" in response.tool_events[0]
    
    assert len(fake_record.recorded) == 1
    user_id, req = fake_record.recorded[0]
    assert user_id == "user-1"
    assert len(req.events) == 1
    evt = req.events[0]
    assert evt.event_type == "quiz_completed"
    assert evt.resource_id == "doc-1"
    assert evt.data["score"] == 0.8
    assert evt.data["total_questions"] == 1
    assert evt.data["rationale"] == "Good answer"
    assert evt.idempotency_key is not None

@pytest.mark.asyncio
async def test_log_conversational_assessment_clamps_score() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("log_conversational_assessment", {"score": 1.5, "rationale": "Too good"}),
            AgentMessage(role="assistant", content="Clamped."),
        ]
    )
    use_case = build_use_case(provider)
    
    class FakeRecordEventsUseCase:
        recorded = []
        async def execute_for_user(self, user_id, request):
            self.recorded.append(request.events[0])
            
    fake_record = FakeRecordEventsUseCase()
    use_case._record_events_batch_use_case = fake_record

    await use_case.execute(
        build_request([TutorChatMessage(role="user", content="Answer.")])
    )

    evt = fake_record.recorded[0]
    assert evt.data["score"] == 1.0  # Clamped

@pytest.mark.asyncio
async def test_log_conversational_assessment_invalid_score() -> None:
    provider = ScriptedChatProvider(
        [
            tool_message("log_conversational_assessment", {"score": "not_a_number", "rationale": ""}),
            AgentMessage(role="assistant", content="Oops."),
        ]
    )
    use_case = build_use_case(provider)
    
    response = await use_case.execute(
        build_request([TutorChatMessage(role="user", content="Answer.")])
    )
    
    # Provider is given the error string
    tool_result = provider.calls[1]["messages"][-1].content
    assert "Tool execution failed: score must be a number" in tool_result


@pytest.mark.asyncio
async def test_global_tutor_tools_restricted() -> None:
    """Verify that global tutor requests do not expose document-bound tools."""
    provider = ScriptedChatProvider([AgentMessage(role="assistant", content="Done")])
    use_case = build_use_case(provider)

    request = TutorChatRequest(
        user_id="user_1",
        document_id=None,
        messages=[TutorChatMessage(role="user", content="help me plan my study")],
    )

    await use_case.execute(request)
    
    # Check the tools passed to provider
    tool_defs = provider.calls[0].get("tools", [])
    if tool_defs:
        tool_names = [t.name for t in tool_defs]
        assert "semantic_search" in tool_names
        assert "get_recommendations" in tool_names
        assert "get_knowledge_state" in tool_names
        assert "generate_flashcard" not in tool_names
        assert "append_note" not in tool_names
        assert "generate_quiz_question" not in tool_names
        assert "log_conversational_assessment" not in tool_names
        assert "query_knowledge_graph" not in tool_names

@pytest.mark.asyncio
async def test_global_tutor_rejects_hallucinated_document_tool() -> None:
    provider = ScriptedChatProvider([
        tool_message("generate_flashcard", {"question": "x", "answer": "y", "difficulty": "easy"}),
        AgentMessage(role="assistant", content="Done")
    ])
    use_case = build_use_case(provider)

    request = TutorChatRequest(
        user_id="user_1",
        document_id=None,
        messages=[TutorChatMessage(role="user", content="help")],
    )

    response = await use_case.execute(request)
    assert any("requires an active document context" in ev for ev in response.tool_events)
