"""Temporary type-checking replacement for the CRLF-broken tutor_chat.py."""

from typing import Any

from persistence.uow_factory import AbstractUnitOfWorkFactory

from application.agent.contracts import TutorChatRequest, TutorChatResponse
from application.exceptions import ApplicationError
from application.interfaces import AuthenticationServiceProtocol, AuthorizationServiceProtocol
from application.retrieval.commands import RetrievalCommand
from application.retrieval.retrieve import RetrieveUseCase
from application.student.get_knowledge_state import GetKnowledgeStateUseCase
from application.student.get_recommendations import GetRecommendationsUseCase
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    AgentMessage,
    ToolCall,
    ToolDefinition,
)

AGENT_TUTOR_CHAT = "agent:tutor:chat"

MAX_ORCHESTRATION_ITERATIONS = 3
MAX_CONVERSATION_MESSAGES = 20
MAX_MESSAGE_LENGTH = 2000
SEARCH_TOP_K = 3
SEARCH_MINIMUM_SIMILARITY = 0.5
MAX_TOOL_LIMIT = 5


class TutorChatUseCase:
    """Bounded, read-only, document-grounded tutoring orchestration loop."""

    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        authorization_service: AuthorizationServiceProtocol,
        retrieve_use_case: RetrieveUseCase,
        provider: AbstractTextGenerationProvider,
        get_recommendations_use_case: GetRecommendationsUseCase,
        get_knowledge_state_use_case: GetKnowledgeStateUseCase,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._authorization_service = authorization_service
        self._retrieve_use_case = retrieve_use_case
        self._provider = provider
        self._get_recommendations_use_case = get_recommendations_use_case
        self._get_knowledge_state_use_case = get_knowledge_state_use_case
        self._uow_factory = uow_factory
        
        from application.analytics.record_events_batch import RecordEventsBatchUseCase
        self._record_events_batch_use_case = RecordEventsBatchUseCase(auth_service=auth_service, uow_factory=uow_factory)


    async def execute(self, request: TutorChatRequest) -> TutorChatResponse:
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
            else:
                session = uow.chat.get_session(session_id, request.user_id)
                if not session:
                    raise ApplicationError("Session not found or permission denied.")
            
            # Persist inbound messages (usually just the newest one)
            for msg in request.messages:
                uow.chat.add_message(
                    ChatMessageEntity(
                        id=str(uuid.uuid4()),
                        session_id=session_id,
                        role=msg.role,
                        content=msg.content,
                        tool_events=None,
                        created_at=datetime.now(UTC),
                    )
                )
            
            # Load bounded history for context
            history = uow.chat.get_messages_for_session(session_id, request.user_id, limit=10)
            uow.commit()

        agent_messages: list[AgentMessage] = [
            AgentMessage(
                role="system",
                content=(
                    "You are Kogniq's interactive AI study tutor. "
                    "Use the semantic_search tool to retrieve relevant chunks.\\n"
                    "You must only answer questions based on the document context.\\n"
                    "If context is insufficient, state that you do not have enough info.\\n"
                    "Never hallucinate citations or content.\\n"
                ),
            )
        ]
        agent_messages.extend(
            AgentMessage(role=m.role, content=m.content) for m in history if m.role in ("user", "assistant")
        )
        tool_defs = self._build_tool_definitions()

        tool_events: list[str] = []
        final_content = "Too many steps taken. Please refine your question."
        for _ in range(MAX_ORCHESTRATION_ITERATIONS):
            response = self._provider.generate_chat(
                messages=agent_messages,
                tools=tool_defs,
                temperature=0.3,
                max_tokens=800,
            )
            agent_messages.append(response)

            if not response.tool_calls:
                final_content = response.content
                break

            for tool_call in response.tool_calls:
                tool_message = await self._dispatch_tool(
                    request.user_id, request.document_id, session_id, tool_call, tool_events
                )
                agent_messages.append(AgentMessage(role="tool", content=tool_message))
        else:
            tool_events.append("Tool call limit reached.")

        with self._uow_factory.create() as uow:
            events_json = json.dumps(tool_events) if tool_events else None
            uow.chat.add_message(
                ChatMessageEntity(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    role="assistant",
                    content=final_content,
                    tool_events=events_json,
                    created_at=datetime.now(UTC),
                )
            )
            uow.commit()

        return TutorChatResponse(
            content=final_content,
            tool_events=tool_events,
            session_id=session_id,
        )

    def _build_tool_definitions(self) -> list[ToolDefinition]:

        return [
            ToolDefinition(
                name="semantic_search",
                description="Search the user's active document for context.",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "The search query."}},
                    "required": ["query"],
                },
            ),
            ToolDefinition(
                name="get_recommendations",
                description="Get user learning recommendations based on spaced repetition.",
                parameters={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max recs (max 5)."}
                    },
                },
            ),
            ToolDefinition(
                name="get_knowledge_state",
                description="Get user knowledge state and mastery score for a resource.",
                parameters={
                    "type": "object",
                    "properties": {"resource_id": {"type": "string", "description": "Resource ID"}},
                    "required": ["resource_id"],
                },
            ),
            ToolDefinition(
                name="log_conversational_assessment",
                description="Record a learning outcome after explicitly asking the learner an assessment question grounded in the active document and evaluating their answer. DO NOT use for casual conversation or unsupported claims. Score must be between 0.0 (incorrect) and 1.0 (perfectly correct).",
                parameters={
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "description": "The correctness of the user's answer (0.0 to 1.0)."},
                        "rationale": {"type": "string", "description": "Brief explanation of why this score was awarded."}
                    },
                    "required": ["score", "rationale"],
                },
            ),
            ToolDefinition(
                name="generate_flashcard",
                description="Propose a targeted flashcard when identifying a useful learning gap. Do not use for casual conversation.",
                parameters={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The front of the flashcard (max 500 chars)."},
                        "answer": {"type": "string", "description": "The back of the flashcard (max 2000 chars)."},
                        "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"], "description": "The expected difficulty of the card."}
                    },
                    "required": ["question", "answer", "difficulty"],
                },
            ),
            ToolDefinition(
                name="generate_quiz_question",
                description="Generate one targeted multiple-choice quiz question when it is pedagogically useful in the current learning conversation. Do not use for casual conversation.",
                parameters={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The quiz question (max 500 chars)."},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Exactly 4 unique options."
                        },
                        "correct_answer": {"type": "string", "description": "The exact string from options that is correct."},
                        "explanation": {"type": "string", "description": "Explanation for the answer (max 500 chars)."},
                        "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"], "description": "The expected difficulty of the question."}
                    },
                    "required": ["question", "options", "correct_answer", "explanation", "difficulty"],
                },
            ),
            ToolDefinition(
                name="append_note",
                description="Propose a durable note for the user's Notebook when a highly valuable learning insight is uncovered during conversation.",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "A short summarizing title (max 100 chars)."},
                        "content": {"type": "string", "description": "The unstructured insight or reflection (max 2000 chars)."},
                    },
                    "required": ["title", "content"],
                },
            ),
        ]

    async def _dispatch_tool(
        self,
        user_id: str,
        document_id: str,
        session_id: str,
        tool_call: ToolCall,
        tool_events: list[str],
    ) -> str:
        """Execute one allowlisted tool call and return the bounded model-facing text."""
        if tool_call.name == "semantic_search":
            return await self._run_semantic_search(
                user_id, document_id, tool_call.arguments, tool_events
            )
        if tool_call.name == "get_recommendations":
            return await self._run_get_recommendations(user_id, tool_call.arguments, tool_events)
        if tool_call.name == "get_knowledge_state":
            return await self._run_get_knowledge_state(user_id, tool_call.arguments, tool_events)
        if tool_call.name == "log_conversational_assessment":
            return await self._run_log_conversational_assessment(
                user_id, document_id, session_id, tool_call, tool_events
            )
        if tool_call.name == "generate_flashcard":
            return self._run_generate_flashcard(session_id, tool_call, tool_events)
        if tool_call.name == "generate_quiz_question":
            return self._run_generate_quiz_question(session_id, tool_call, tool_events)
        if tool_call.name == "append_note":
            return self._run_append_note(session_id, tool_call, tool_events)
        return "Error: Unknown tool."

    def _run_generate_quiz_question(
        self,
        session_id: str,
        tool_call: ToolCall,
        tool_events: list[str],
    ) -> str:
        question = str(tool_call.arguments.get("question", ""))[:500]
        options = tool_call.arguments.get("options", [])
        if not isinstance(options, list):
            options = []
        options = [str(o)[:200] for o in options]
        correct_answer = str(tool_call.arguments.get("correct_answer", ""))[:200]
        explanation = str(tool_call.arguments.get("explanation", ""))[:500]
        difficulty = tool_call.arguments.get("difficulty", "medium")
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"

        idempotency_key = f"{session_id}_{tool_call.id}"

        import json

        proposal = {
            "type": "quiz_proposal",
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "difficulty": difficulty,
            "idempotency_key": idempotency_key,
        }

        tool_events.append(json.dumps(proposal))

        return "I have proposed the quiz question to the user. Do not assume it is saved yet. Wait for their confirmation."

    def _run_generate_flashcard(
        self,
        session_id: str,
        tool_call: ToolCall,
        tool_events: list[str],
    ) -> str:
        question = str(tool_call.arguments.get("question", ""))[:500]
        answer = str(tool_call.arguments.get("answer", ""))[:2000]
        difficulty = tool_call.arguments.get("difficulty", "medium")
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"
            
        import json
        proposal = {
            "type": "flashcard_proposal",
            "question": question,
            "answer": answer,
            "difficulty": difficulty,
            "idempotency_key": f"{session_id}_{tool_call.id}"
        }
        tool_events.append(json.dumps(proposal))
        return "Flashcard proposed successfully. Waiting for user confirmation."

    def _run_append_note(
        self,
        session_id: str,
        tool_call: ToolCall,
        tool_events: list[str],
    ) -> str:
        title = str(tool_call.arguments.get("title", ""))[:100]
        content = str(tool_call.arguments.get("content", ""))[:2000]

        import json
        proposal = {
            "type": "note_proposal",
            "title": title,
            "content": content,
            "idempotency_key": f"{session_id}_{tool_call.id}"
        }
        tool_events.append(json.dumps(proposal))
        return "Note proposed successfully. Waiting for user confirmation."

    async def _run_semantic_search(
        self,
        user_id: str,
        document_id: str,
        arguments: dict[str, Any],
        tool_events: list[str],
    ) -> str:
        query = arguments.get("query", "")
        tool_events.append(f"Searched document for: '{query}'")
        try:
            command = RetrievalCommand(
                user_id=user_id,
                document_id=document_id,
                query=query,
                top_k=SEARCH_TOP_K,
                minimum_similarity=SEARCH_MINIMUM_SIMILARITY,
            )
            result = await self._retrieve_use_case.execute(command)
            chunks_text = "\n\n".join(
                f"Chunk {i + 1}:\n{r.content}" for i, r in enumerate(result.results)
            )
            if not chunks_text.strip():
                chunks_text = "No relevant content found in this document."
            return chunks_text
        except Exception as e:
            return f"Tool execution failed: {e}"

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

    async def _run_get_recommendations(
        self,
        user_id: str,
        arguments: dict[str, Any],
        tool_events: list[str],
    ) -> str:
        limit = MAX_TOOL_LIMIT
        if "limit" in arguments:
            raw_limit = arguments["limit"]
            if isinstance(raw_limit, bool):
                tool_events.append("Tool execution failed: limit must be an int.")
                return "Tool execution failed: limit must be an int."
            try:
                limit_val = int(raw_limit)
            except (ValueError, TypeError):
                tool_events.append("Tool execution failed: limit must be an int.")
                return "Tool execution failed: limit must be an int."
            if limit_val < 1 or limit_val > MAX_TOOL_LIMIT:
                tool_events.append("Tool execution failed: limit must be between 1 and 5.")
                return "Tool execution failed: limit must be between 1 and 5."
            limit = limit_val

        tool_events.append("Retrieved learning recommendations.")
        try:
            response = await self._get_recommendations_use_case.execute_for_user(
                user_id=user_id, limit=limit
            )
            if not response.recommendations:
                return "No current recommendations found."
            return "\n".join(
                f"- Resource '{r.resource_title}' (ID: {r.resource_id}): "
                f"{r.action_type} (Priority: {r.priority_score:.2f}) - {r.reason}"
                for r in response.recommendations
            )
        except Exception as e:
            return f"Tool execution failed: {e}"

    async def _run_get_knowledge_state(
        self,
        user_id: str,
        arguments: dict[str, Any],
        tool_events: list[str],
    ) -> str:
        resource_id = arguments.get("resource_id", "")
        if not isinstance(resource_id, str) or not resource_id.strip():
            tool_events.append("Tool execution failed: Missing or invalid resource_id.")
            return "Tool execution failed: Missing or invalid resource_id."

        tool_events.append("Retrieved knowledge state for resource.")
        try:
            response = await self._get_knowledge_state_use_case.execute_for_user(
                user_id=user_id, resource_id=resource_id.strip()
            )
            if response.state is None:
                return f"State not found for resource '{resource_id}'."
            state = response.state
            last_reviewed = (
                state.last_reviewed_at.isoformat() if state.last_reviewed_at else "Never"
            )
            next_review = state.next_review_due.isoformat() if state.next_review_due else "None"
            return (
                f"Resource ID: {state.resource_id}\n"
                f"Mastery Score: {state.mastery_score:.2f}\n"
                f"Last Review: {last_reviewed}\n"
                f"Next Review Due: {next_review}"
            )
        except Exception as e:
            return f"Tool execution failed: {e}"




