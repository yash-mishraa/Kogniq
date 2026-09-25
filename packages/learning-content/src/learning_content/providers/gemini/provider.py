import logging
from typing import Any

from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    AgentMessage,
    TextGenerationProviderInfo,
    ToolCall,
    ToolDefinition,
)

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None  # type: ignore

logger = logging.getLogger(__name__)


class GeminiTextGenerationProvider(AbstractTextGenerationProvider):
    """Text generation provider using Google Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.1-flash-lite",
    ) -> None:
        if genai is None:
            raise ImportError("google-genai is not installed. Please install it to use Gemini.")

        self.api_key = api_key
        self.model_name = model_name
        self._client: genai.Client | None = None

        self._info = TextGenerationProviderInfo(
            provider_id="gemini",
            provider_name="Google Gemini",
            default_model=model_name,
            model_version="3.1",
            context_window=2_000_000,
            supports_streaming=True,
            supports_json=True,
            supports_images=True,
            supports_tools=True,
        )

    @property
    def client(self) -> "genai.Client":
        """Lazy initialization of the Gemini client."""
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @property
    def info(self) -> TextGenerationProviderInfo:
        return self._info

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text using Gemini."""
        from typing import Any

        config_kwargs: dict[str, Any] = {}
        if temperature is not None:
            config_kwargs["temperature"] = temperature
        if max_tokens is not None:
            config_kwargs["max_output_tokens"] = max_tokens

        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise RuntimeError(f"Gemini generation failed: {e}") from e

    def generate_chat(
        self,
        messages: list[AgentMessage],
        tools: list[ToolDefinition] | None = None,
        system_instruction: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AgentMessage:
        from learning_content.providers.base import AgentMessage, ToolCall

        gemini_messages = []
        for m in messages:
            parts = []
            if m.content:
                parts.append(types.Part.from_text(text=m.content))
            for tc in m.tool_calls:
                parts.append(types.Part.from_function_call(name=tc.name, args=tc.arguments))
            if m.role == "tool":
                parts.append(
                    types.Part.from_function_response(name="tool", response={"result": m.content})
                )
            role = "user" if m.role == "user" or m.role == "tool" else "model"
            gemini_messages.append(types.Content(role=role, parts=parts))

        gemini_tools = []
        if tools:
            for t in tools:
                gemini_tools.append(
                    types.Tool(
                        function_declarations=[
                            types.FunctionDeclaration(
                                name=t.name,
                                description=t.description,
                                parameters=t.parameters,  # type: ignore
                            )
                        ]
                    )
                )

        config_kwargs: dict[str, Any] = {}
        if gemini_tools:
            config_kwargs["tools"] = gemini_tools
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=gemini_messages,
            config=config,
        )

        tool_calls = []
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

        return AgentMessage(role="assistant", content=response.text or "", tool_calls=tool_calls, usage=usage)
