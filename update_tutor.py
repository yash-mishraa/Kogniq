import sys
import re

with open('packages/application/src/application/agent/tutor_chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the start of execute with telemetry setup
replacement_execute = '''    async def execute(self, request: TutorChatRequest) -> TutorChatResponse:
        import time
        from shared.logging.context import update_telemetry_context
        import logging
        logger = logging.getLogger(__name__)

        auth_result = await self._authorization_service.require_permission(
            request.user_id, AGENT_TUTOR_CHAT
        )
        if not auth_result.allowed:
            raise ApplicationError(f"Permission denied: {auth_result.reason}")

        if len(request.messages) > MAX_CONVERSATION_MESSAGES:
            raise ApplicationError("Conversation history exceeds maximum allowed messages.")
        if any(len(m.content) > MAX_MESSAGE_LENGTH for m in request.messages):
            raise ApplicationError("Individual message exceeds maximum length.")

        import json
        import uuid
        from datetime import UTC, datetime

        from persistence.repositories.chat import ChatMessageEntity, ChatSessionEntity

        session_id = request.session_id
        now = datetime.now(UTC)

        with self._uow_factory.create() as uow:
            session = None
            if not session_id:
                session_id = str(uuid.uuid4())
                uow.chat.create_session(
                    ChatSessionEntity(
                        id=session_id,
                        user_id=request.user_id,
                        document_id=request.document_id,
                        title=None,
                        created_at=now,
                        updated_at=now,
                    )
                )
                active_document_id = request.document_id
            else:
                session = uow.chat.get_session(session_id, request.user_id)
                if not session:
                    raise ApplicationError(f"Session {session_id} not found or access denied.")
                active_document_id = session.document_id
        
        # Telemetry
        update_telemetry_context(user_id=request.user_id, session_id=session_id)
        start_time = time.monotonic()
        logger.info(
            "tutor_request_started",
            extra={"context_type": "document" if active_document_id else "global"}
        )'''

content = re.sub(r'    async def execute\(self, request: TutorChatRequest\) -> TutorChatResponse:.*?active_document_id = session.document_id', replacement_execute, content, flags=re.DOTALL)


# I will replace the iteration and final return
replacement_loop = '''            logger.info("tutor_iteration_started", extra={"iteration": i})

            # Retrieve available tools based on context
            available_tools = self._get_available_tools(active_document_id is not None)
            
            gen_start_time = time.monotonic()
            try:
                # Ask the provider
                response_message = self._provider.generate_chat(
                    messages=agent_messages,
                    tools=available_tools,
                    system_instruction=system_instruction,
                    temperature=TEMPERATURE,
                )
                gen_duration = (time.monotonic() - gen_start_time) * 1000
                
                usage = getattr(response_message, "usage", None)
                usage_dict = {}
                if usage:
                    if usage.prompt_tokens is not None:
                        usage_dict["prompt_tokens"] = usage.prompt_tokens
                    if usage.completion_tokens is not None:
                        usage_dict["completion_tokens"] = usage.completion_tokens
                    if usage.total_tokens is not None:
                        usage_dict["total_tokens"] = usage.total_tokens

                logger.info(
                    "provider_generation_completed",
                    extra={
                        "provider": self._provider.info.provider_name,
                        "model": self._provider.info.default_model,
                        "duration_ms": gen_duration,
                        "status": "success",
                        **usage_dict
                    }
                )
            except Exception as e:
                gen_duration = (time.monotonic() - gen_start_time) * 1000
                logger.error(
                    "provider_generation_failed",
                    extra={
                        "provider": self._provider.info.provider_name,
                        "model": self._provider.info.default_model,
                        "duration_ms": gen_duration,
                        "status": "failure",
                        "failure_category": "provider_error"
                    }
                )
                raise ApplicationError(f"Provider generation failed: {e}") from e

            # Save the assistant's message immediately if there's content or tool calls
'''
content = re.sub(r'            # Retrieve available tools based on context.*?# Save the assistant\'s message immediately if there\'s content or tool calls', replacement_loop, content, flags=re.DOTALL)


# At the end of execute
replacement_end = '''        duration_ms = (time.monotonic() - start_time) * 1000
        logger.info(
            "tutor_request_completed",
            extra={
                "duration_ms": duration_ms,
                "status": "success",
                "iteration_count": i + 1,
            }
        )

        return TutorChatResponse(
            content=final_text,
            tool_events=tool_events,
            session_id=session_id,
        )'''
content = re.sub(r'        return TutorChatResponse\(\s*content=final_text,\s*tool_events=tool_events,\s*session_id=session_id,\s*\)', replacement_end, content, flags=re.DOTALL)


with open('packages/application/src/application/agent/tutor_chat.py', 'w', encoding='utf-8') as f:
    f.write(content)

