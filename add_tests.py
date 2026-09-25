import sys

with open('apps/api/tests/test_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_tests = """
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
"""

content += new_tests

with open('apps/api/tests/test_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
