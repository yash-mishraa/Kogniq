import sys
import re

with open('packages/learning-content/src/learning_content/providers/mock/provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''        from learning_content.providers.base import ProviderUsage
        usage = ProviderUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        
        # After a tool result, ground the answer in the retrieved context.
        if messages and messages[-1].role == "tool":
            return AgentMessage(
                role="assistant",
                content=f"Based on the document context: {messages[-1].content}",
                usage=usage
            )

        # Otherwise, issue one deterministic semantic search against the latest
        # user message, mirroring how a real provider uses the tool allowlist.
        last_user_content = next(
            (m.content for m in reversed(messages) if m.role == "user"),
            "",
        )
        return AgentMessage(
            role="assistant",
            content="",
            tool_calls=[
                ToolCall(
                    id="mock_call_1",
                    name="semantic_search",
                    arguments={"query": last_user_content},
                )
            ],
            usage=usage
        )'''

content = re.sub(r'        # After a tool result, ground the answer in the retrieved context.*?usage=usage\)', replacement, content, flags=re.DOTALL)

with open('packages/learning-content/src/learning_content/providers/mock/provider.py', 'w', encoding='utf-8') as f:
    f.write(content)
