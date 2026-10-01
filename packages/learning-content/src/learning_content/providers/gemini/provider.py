import logging
import random
import time
from collections.abc import Callable
from typing import Any, TypeVar

from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    AgentMessage,
    ProviderUsage,
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

T = TypeVar("T")


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

    def _execute_with_retry(self, operation: Callable[[], T]) -> T:
        """
        Bounded retry policy specifically at the provider adapter boundary.
        Prevents full orchestration iteration duplication.
        """
        max_attempts = 3
        base_delay = 1.0

        for attempt in range(1, max_attempts + 1):
            try:
                return operation()
            except Exception as e:
                # Classify the exception
                is_timeout = isinstance(e, TimeoutError) or "timeout" in str(e).lower()
                is_api_error = e.__class__.__name__ == "APIError"

                code = getattr(e, "code", None)
                retryable = is_timeout or (is_api_error and code in (429, 500, 502, 503, 504))

                if is_timeout:
                    # M1 Telemetry: Provider Timeout
                    logger.warning(
                        "Gemini provider timeout", extra={"provider_timeout": {"elapsed_ms": 30000}}
                    )

                if not retryable or attempt == max_attempts:
                    # M1 Telemetry: Terminal Provider Failure
                    logger.error(
                        "Gemini provider permanent failure or retry exhaustion",
                        extra={
                            "provider_failed": {
                                "failure_category": "timeout" if is_timeout else "api_error",
                                "terminal": True,
                                "code": code,
                            }
                        },
                    )
                    raise RuntimeError(f"Gemini generation failed: {e}") from e

                # Bounded Exponential backoff with jitter
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)

                # M1 Telemetry: Provider Retry
                logger.warning(
                    f"Transient provider error, retrying in {delay:.2f}s",
                    extra={
                        "provider_retry_attempt": {
                            "attempt_number": attempt,
                            "delay_ms": int(delay * 1000),
                            "exception_class": e.__class__.__name__,
                            "code": code,
                        }
                    },
                )
                time.sleep(delay)

        raise RuntimeError("Unreachable")

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text using Gemini."""
        config_kwargs: dict[str, Any] = {}
        if temperature is not None:
            config_kwargs["temperature"] = temperature
        if max_tokens is not None:
            config_kwargs["max_output_tokens"] = max_tokens

        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        def _do_generate() -> str:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            return response.text or ""

        return self._execute_with_retry(_do_generate)

    def generate_chat(
        self,
        messages: list[AgentMessage],
        tools: list[ToolDefinition] | None = None,
        system_instruction: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AgentMessage:
        gemini_messages = []
        for m in messages:
            parts = []
            if m.content:
                parts.append(types.Part.from_text(text=m.content))
            parts.extend(
                types.Part.from_function_call(name=tc.name, args=tc.arguments)
                for tc in m.tool_calls
            )
            if m.role == "tool":
                parts.append(
                    types.Part.from_function_response(name="tool", response={"result": m.content})
                )
            role = "user" if m.role == "user" or m.role == "tool" else "model"
            gemini_messages.append(types.Content(role=role, parts=parts))

        gemini_tools = []
        if tools:
            gemini_tools.extend(
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=t.name,
                            description=t.description,
                            parameters=t.parameters,  # type: ignore
                        )
                    ]
                )
                for t in tools
            )

        config_kwargs: dict[str, Any] = {}
        if gemini_tools:
            config_kwargs["tools"] = gemini_tools
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if temperature is not None:
            config_kwargs["temperature"] = temperature
        if max_tokens is not None:
            config_kwargs["max_output_tokens"] = max_tokens

        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        def _do_generate_chat() -> AgentMessage:
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
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = ProviderUsage(
                    prompt_tokens=getattr(response.usage_metadata, "prompt_token_count", None),
                    completion_tokens=getattr(
                        response.usage_metadata, "candidates_token_count", None
                    ),
                    total_tokens=getattr(response.usage_metadata, "total_token_count", None),
                )

            return AgentMessage(
                role="assistant",
                content=response.text or "",
                tool_calls=tool_calls,
                usage=usage,
            )

        return self._execute_with_retry(_do_generate_chat)
