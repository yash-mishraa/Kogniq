from types import SimpleNamespace
from typing import Any

from persistence.factory import MemoryRepositoryFactory
from persistence.memory_uow import MemoryUnitOfWork
from persistence.uow_factory import AbstractUnitOfWorkFactory

from application.agent.tutor_chat import TutorChatUseCase
from application.retrieval.commands import RetrievalCommand
from learning_content.providers.base import AgentMessage, ToolDefinition


class ScriptedChatProvider:
    def __init__(self, responses: list[AgentMessage]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.generated_messages: list[AgentMessage] = []

    def generate_chat(
        self,
        messages: list[AgentMessage],
        tools: list[ToolDefinition] | None = None,
        system_instruction: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AgentMessage:
        self.calls.append({'messages': list(messages), 'tools': tools})
        del system_instruction, temperature, max_tokens
        res = self._responses.pop(0)
        if res.content == "RAISE_API_ERROR":
            from google.genai.errors import APIError
            raise APIError("Fake API Error", code=503)
        if res.content == "RAISE_TIMEOUT":
            raise TimeoutError("Fake Provider timeout")
        self.generated_messages.append(res)
        return res

class FakeAuthorizationService:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed

    async def require_permission(self, user_id: str, permission_id: str) -> Any:
        del user_id, permission_id
        reason = 'Fake logic' if not self.allowed else None
        return SimpleNamespace(allowed=self.allowed, reason=reason)

class FakeRetrieveUseCase:
    def __init__(self, contents: list[str] | None = None) -> None:
        self.commands: list[RetrievalCommand] = []
        self._contents = contents if contents is not None else []

    async def execute(self, command: RetrievalCommand) -> Any:
        from application.retrieval.responses import RetrievalResult, ChunkData
        self.commands.append(command)
        results = [
            ChunkData(
                chunk_id=f"chk-{i}",
                document_id=command.document_id or 'doc-1',
                content=c,
                chunk_index=i,
                score=0.9
            ) for i, c in enumerate(self._contents)
        ]
        return RetrievalResult(
            status="completed",
            query=command.query,
            document_id=command.document_id or 'doc-1',
            total_results=len(results),
            results=results
        )

class FakeRecommendationsUseCase:
    def __init__(self, titles: list[str]) -> None:
        self._titles = titles

    async def execute_for_user(self, user_id: str, limit: int = 5) -> Any:
        del user_id
        recs = [SimpleNamespace(title=t) for t in self._titles[:limit]]
        return SimpleNamespace(recommendations=recs)

class FakeKnowledgeStateUseCase:
    def __init__(self) -> None:
        self.last_resource_id: str | None = None

    async def execute_for_user(self, user_id: str, resource_id: str) -> Any:
        del user_id
        self.last_resource_id = resource_id
        return SimpleNamespace(
            state=SimpleNamespace(
                resource_id=resource_id,
                mastery_score=0.75,
                knowledge_components=[]
            )
        )

class FakeUowFactory(AbstractUnitOfWorkFactory):
    def __init__(self) -> None:
        self._factory = MemoryRepositoryFactory()

    def create(self) -> MemoryUnitOfWork:
        return MemoryUnitOfWork(self._factory)

def build_use_case(
    provider: Any,
    *,
    allowed: bool = True,
    retrieve: FakeRetrieveUseCase | None = None,
    recommendations: FakeRecommendationsUseCase | None = None,
    knowledge_state: FakeKnowledgeStateUseCase | None = None,
    uow_factory: FakeUowFactory | None = None,
) -> TutorChatUseCase:
    return TutorChatUseCase(
        auth_service=SimpleNamespace(),
        authorization_service=FakeAuthorizationService(allowed), # type: ignore
        retrieve_use_case=retrieve or FakeRetrieveUseCase(),  # type: ignore
        provider=provider,
        get_recommendations_use_case=recommendations or FakeRecommendationsUseCase([]),  # type: ignore
        get_knowledge_state_use_case=knowledge_state or FakeKnowledgeStateUseCase(),  # type: ignore
        uow_factory=uow_factory or FakeUowFactory(),
    )

import time

from apps.api.app.middleware.benchmark import benchmark_metrics_var

class DeterministicLatencyProvider:
    def generate_chat(self, messages, tools=None, system_instruction=None, **kwargs):
        return self._execute_with_retry(lambda: self._do_generate_chat(messages, tools, system_instruction, **kwargs))

    def __init__(self, delay_ms: float = 1000.0) -> None:
        self.delay_ms = delay_ms
        self.calls = []

    def _do_generate_chat(self, messages, tools, system_instruction, **kwargs):
        self.calls.append(messages)
        start = time.perf_counter()
        time.sleep(self.delay_ms / 1000.0)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        
        # Append duration to context var safely
        pass
            
        last_msg = messages[-1].content if messages and messages[-1].content else ""
        if "M3_INJECT_TIMEOUT_ALL" in last_msg:
            raise TimeoutError("Simulated timeout exhaustion")
        
        if "M3_INJECT_TIMEOUT_ONCE" in last_msg:
            # Check how many times we've been called for this specific instruction
            call_count = sum(1 for call in self.calls if call and call[-1].content and "M3_INJECT_TIMEOUT_ONCE" in call[-1].content)
            if call_count % 2 != 0:
                raise TimeoutError("Simulated timeout once")

        return AgentMessage(role="assistant", content="Simulated deterministic response")

    def _execute_with_retry(self, operation):
        max_attempts = 3
        base_delay = 0.1
        for attempt in range(1, max_attempts + 1):
            try:
                return operation()
            except TimeoutError as e:
                if attempt == max_attempts:
                    raise RuntimeError(f"Generation failed: {e}") from e
                time.sleep(base_delay)
        raise RuntimeError("Unreachable")

