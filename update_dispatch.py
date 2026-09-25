import sys
import re

with open('packages/application/src/application/agent/tutor_chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    async def _dispatch_tool(
        self,
        user_id: str,
        document_id: str | None,
        session_id: str,
        tool_call: ToolCall,
        tool_events: list[str],
    ) -> str:'''

content = re.sub(r'    async def _dispatch_tool\(\s*self,\s*tool_call: ToolCall,\s*user_id: str,\s*document_id: str \| None,\s*session_id: str,\s*tool_events: list\[str\],\s*\) -> str:', replacement, content, flags=re.DOTALL)

with open('packages/application/src/application/agent/tutor_chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
