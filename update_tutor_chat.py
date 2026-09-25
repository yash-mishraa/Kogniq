import sys
import json

with open("packages/application/src/application/agent/tutor_chat.py", "r", encoding="utf-8") as f:
    content = f.read()

if 'name="generate_flashcard"' not in content:
    tool_def = """            ToolDefinition(
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
        ]"""
    content = content.replace("            ),\n        ]", tool_def)

dispatch_block = """        if tool_call.name == "log_conversational_assessment":
            return await self._run_log_conversational_assessment(
                user_id, document_id, session_id, tool_call, tool_events
            )
        if tool_call.name == "generate_flashcard":
            return self._run_generate_flashcard(session_id, tool_call, tool_events)"""

content = content.replace(
"""        if tool_call.name == "log_conversational_assessment":
            return await self._run_log_conversational_assessment(
                user_id, document_id, session_id, tool_call, tool_events
            )""", dispatch_block
)

run_generate = """    def _run_generate_flashcard(
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

    async def _run_semantic_search("""

content = content.replace("    async def _run_semantic_search(", run_generate)

with open("packages/application/src/application/agent/tutor_chat.py", "w", encoding="utf-8") as f:
    f.write(content)
