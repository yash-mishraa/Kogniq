import sys

with open('packages/application/src/application/agent/tutor_chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_method = """
    async def _run_log_conversational_assessment(
        self,
        user_id: str,
        document_id: str,
        session_id: str,
        tool_call: ToolCall,
        tool_events: list[str],
    ) -> str:
        score = tool_call.arguments.get("score")
        rationale = tool_call.arguments.get("rationale", "")

        if score is None or not isinstance(score, (int, float)):
            msg = "Tool execution failed: score must be a number between 0.0 and 1.0."
            tool_events.append(msg)
            return msg

        # Clamp safely
        score = max(0.0, min(1.0, float(score)))

        from application.analytics.record_events_batch import EventPayload, RecordEventsBatchRequest

        payload = EventPayload(
            event_id=str(tool_call.id) + "-evt",
            event_type="quiz_completed",
            resource_id=document_id,
            data={"score": score, "total_questions": 1, "rationale": rationale},
            idempotency_key=f"{session_id}_{tool_call.id}"
        )
        
        request = RecordEventsBatchRequest(token="", events=[payload])

        try:
            await self._record_events_batch_use_case.execute_for_user(user_id, request)
        except Exception as e:
            msg = f"Tool execution failed: {e}"
            tool_events.append(msg)
            return msg

        tool_events.append(f"Logged conversational assessment (Score: {score:.2f})")

        # Fetch updated mastery
        try:
            state_response = await self._get_knowledge_state_use_case.execute_for_user(
                user_id=user_id, resource_id=document_id
            )
            if state_response.state:
                return f"Successfully logged assessment (Score: {score:.2f}). Current Mastery Score is now {state_response.state.mastery_score:.2f}."
        except Exception:
            pass

        return f"Successfully logged assessment (Score: {score:.2f})."
"""

# Find the end of _run_get_knowledge_state
import re
match = re.search(r"        except Exception as e:\n            return f\"Tool execution failed: \{e\}\"\n", content)
if match:
    insert_pos = match.end()
    content = content[:insert_pos] + new_method + content[insert_pos:]
    with open('packages/application/src/application/agent/tutor_chat.py', 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("Could not find insertion point.")
