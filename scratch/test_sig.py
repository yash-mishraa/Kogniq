import os
import json
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
tools = [types.Tool(function_declarations=[
    types.FunctionDeclaration(name="search", description="search", parameters={"type": "object", "properties": {"q": {"type": "string"}}})
])]
config = types.GenerateContentConfig(tools=tools, automatic_function_calling={"disable": True})
resp = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Search for 'test'",
    config=config
)

part = resp.candidates[0].content.parts[0]
print(part)
