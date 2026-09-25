import sys

with open('packages/learning-content/src/learning_content/providers/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement1 = '''@dataclass
class ProviderUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

@dataclass
class ToolDefinition:'''

content = content.replace('@dataclass\nclass ToolDefinition:', replacement1, 1)

replacement2 = '''@dataclass
class AgentMessage:
    role: str
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: ProviderUsage | None = None'''

content = content.replace('@dataclass\nclass AgentMessage:\n    role: str\n    content: str\n    tool_calls: list[ToolCall] = field(default_factory=list)', replacement2, 1)

with open('packages/learning-content/src/learning_content/providers/base.py', 'w', encoding='utf-8') as f:
    f.write(content)
