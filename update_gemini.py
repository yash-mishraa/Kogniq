import sys
import re

with open('packages/learning-content/src/learning_content/providers/gemini/provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''        tool_calls = []
        if response.function_calls:
            for fc in response.function_calls:
                name = fc.name or ""
                args = dict(fc.args) if fc.args else {}
                tool_calls.append(ToolCall(id=name, name=name, arguments=args))
        
        usage = None
        from learning_content.providers.base import ProviderUsage
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = ProviderUsage(
                prompt_tokens=getattr(response.usage_metadata, "prompt_token_count", None),
                completion_tokens=getattr(response.usage_metadata, "candidates_token_count", None),
                total_tokens=getattr(response.usage_metadata, "total_token_count", None)
            )

        return AgentMessage(role="assistant", content=response.text or "", tool_calls=tool_calls, usage=usage)'''

content = re.sub(r'        tool_calls = \[\]\s*if response.function_calls:.*?return AgentMessage\(role="assistant", content=response\.text or "", tool_calls=tool_calls\)', replacement, content, flags=re.DOTALL)

with open('packages/learning-content/src/learning_content/providers/gemini/provider.py', 'w', encoding='utf-8') as f:
    f.write(content)
