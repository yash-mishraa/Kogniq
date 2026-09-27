from evaluation.harness.fakes import ScriptedChatProvider, build_use_case
from evaluation.models.eval_case import EvalCase

from application.agent.contracts import TutorChatMessage, TutorChatRequest
from learning_content.providers.base import AgentMessage, ToolCall


class TutorEvaluationHarness:
    async def evaluate(self, case: EvalCase) -> None:
        # Construct responses
        responses = []
        for r in case.scripted_provider.responses:
            tool_calls = [
                ToolCall(id="call-mock", name=tc.name, arguments=tc.arguments)
                for tc in r.tool_calls
            ]
            responses.append(AgentMessage(role=r.role, content=r.content, tool_calls=tool_calls))
        
        from datetime import UTC, datetime

        from evaluation.harness.fakes import FakeUowFactory
        from persistence.repositories.chat import ChatSessionEntity
        
        provider = ScriptedChatProvider(responses)
        uow_factory = FakeUowFactory()
        
        # Seed the session so it exists in memory
        with uow_factory.create() as uow:
            uow.chat.create_session(ChatSessionEntity(title="Eval Session",
                id=case.context.session_id,
                user_id=case.context.user_id,
                document_id=case.context.document_id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            ))
            uow.commit()

        from evaluation.harness.fakes import FakeRetrieveUseCase
        retrieve_use_case = FakeRetrieveUseCase(case.context.retrieved_chunks) if getattr(case.context, "retrieved_chunks", None) is not None else None
        use_case = build_use_case(provider, uow_factory=uow_factory, retrieve=retrieve_use_case)
        
        request = TutorChatRequest(
            user_id=case.context.user_id,
            document_id=case.context.document_id,
            session_id=case.context.session_id,
            messages=[
                TutorChatMessage(role=m['role'], content=m['content'])
                for m in case.input.messages
            ]
        )
        
        exception = None
        response = None
        try:
            response = await use_case.execute(request)
        except Exception as e:
            exception = e
        
        # Evaluate expectations
        if case.expected.exception:
            assert exception is not None, \
                f"Expected exception {case.expected.exception} but none was raised"
            assert case.expected.exception in str(exception), \
                f"Exception '{exception}' missing '{case.expected.exception}'"
        else:
            assert exception is None, f"Unexpected exception raised: {exception}"
        
        if case.expected.tool_calls_attempted is not None:
            actual_tools = []
            if getattr(provider, 'generated_messages', None):
                for msg in provider.generated_messages:
                    if msg.role == 'assistant' and msg.tool_calls:
                        actual_tools.extend([tc.name for tc in msg.tool_calls])
            
            exp_tools = case.expected.tool_calls_attempted
            assert actual_tools == exp_tools, \
                f"Attempted {actual_tools} != {exp_tools}"
            
        if case.expected.response_includes is not None:
            assert response is not None, "Response was None"
            assert case.expected.response_includes in response.content, \
                f"Response missing '{case.expected.response_includes}'"
