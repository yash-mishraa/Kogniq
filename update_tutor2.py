import sys
import re

with open('packages/application/src/application/agent/tutor_chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    async def _dispatch_tool(
        self,
        tool_call: ToolCall,
        user_id: str,
        document_id: str | None,
        session_id: str,
        tool_events: list[str],
    ) -> str:
        import time
        import logging
        logger = logging.getLogger(__name__)

        logger.info(
            "tutor_tool_called",
            extra={
                "tool_name": tool_call.name,
                "session_id": session_id,
            }
        )
        start_time = time.monotonic()
        status = "success"
        failure_category = None
        
        try:
            if not document_id and tool_call.name in {
                "generate_flashcard",
                "append_note",
                "generate_quiz_question",
                "log_conversational_assessment",
                "query_knowledge_graph",
            }:
                msg = f"Tool '{tool_call.name}' is only available when chatting about a specific document."
                tool_events.append(msg)
                status = "failure"
                failure_category = "invalid_tool_call"
                return msg

            if tool_call.name == "generate_flashcard":
                result = await self._run_generate_flashcard(tool_call, session_id, tool_events)
            elif tool_call.name == "append_note":
                result = await self._run_append_note(tool_call, session_id, tool_events)
            elif tool_call.name == "generate_quiz_question":
                result = await self._run_generate_quiz_question(tool_call, session_id, tool_events)
            elif tool_call.name == "semantic_search":
                result = await self._run_semantic_search(user_id, document_id, tool_call.arguments, tool_events)
            elif tool_call.name == "log_conversational_assessment":
                assert document_id is not None
                result = await self._run_log_conversational_assessment(
                    user_id, document_id, session_id, tool_call, tool_events
                )
            elif tool_call.name == "get_learning_recommendations":
                result = await self._run_get_recommendations(user_id, tool_call.arguments, tool_events)
            elif tool_call.name == "get_knowledge_state":
                result = await self._run_get_knowledge_state(user_id, tool_call.arguments, tool_events)
            elif tool_call.name == "query_knowledge_graph":
                assert document_id is not None
                result = await self._run_query_knowledge_graph(
                    user_id, document_id, tool_call, tool_events
                )
            else:
                msg = f"Unknown tool: {tool_call.name}"
                tool_events.append(msg)
                status = "failure"
                failure_category = "invalid_tool_call"
                result = msg
                
            if "Tool execution failed" in result:
                status = "failure"
                failure_category = "tool_execution_error"
                
            return result
        except Exception as e:
            status = "failure"
            failure_category = "unknown_error"
            raise
        finally:
            duration_ms = (time.monotonic() - start_time) * 1000
            if status == "success":
                logger.info(
                    "tutor_tool_completed",
                    extra={
                        "tool_name": tool_call.name,
                        "duration_ms": duration_ms,
                        "status": status,
                    }
                )
            else:
                logger.error(
                    "tutor_tool_failed",
                    extra={
                        "tool_name": tool_call.name,
                        "duration_ms": duration_ms,
                        "status": status,
                        "failure_category": failure_category,
                    }
                )'''

content = re.sub(r'    async def _dispatch_tool\(.*?def _run_generate_flashcard', replacement + '\n\n    async def _run_generate_flashcard', content, flags=re.DOTALL)

with open('packages/application/src/application/agent/tutor_chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
