import sys
import re

with open('packages/application/src/application/agent/tutor_chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'msg = f"Tool \'{tool_call.name}\' is only available when chatting about a specific document."',
    'msg = "Tool execution failed: This tool requires an active document context."'
)
content = content.replace(
    'elif tool_call.name == "get_learning_recommendations":',
    'elif tool_call.name == "get_recommendations":'
)

with open('packages/application/src/application/agent/tutor_chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
