import sys

with open('apps/api/tests/test_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'assert tool_names == {"semantic_search", "get_recommendations", "get_knowledge_state"}',
    'assert tool_names == {"semantic_search", "get_recommendations", "get_knowledge_state", "log_conversational_assessment"}'
)

with open('apps/api/tests/test_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
