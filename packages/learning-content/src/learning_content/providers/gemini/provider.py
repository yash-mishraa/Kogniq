import logging
import os
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
    from google.genai import errors, types
except ImportError:
    genai = None  # type: ignore
    errors = None  # type: ignore
    types = None  # type: ignore

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GeminiTextGenerationProvider(AbstractTextGenerationProvider):
    """Text generation provider using Google Gemini with bounded retry, jitter, and circuit breaker."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
    ) -> None:
        if genai is None:
            raise ImportError("google-genai is not installed. Please install it to use Gemini.")

        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        # Ensure deprecated models are redirected to supported active version
        if model_name in ("gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"):
            model_name = "gemini-3.5-flash-lite"
        self.model_name = model_name
        self._client: genai.Client | None = None

        # Circuit breaker state
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0
        self._failure_threshold = 3
        self._cooldown_seconds = 30.0

        self._info = TextGenerationProviderInfo(
            provider_id="gemini",
            provider_name="Google Gemini",
            default_model=model_name,
            model_version="2.5",
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

    def _is_transient(self, e: Exception) -> bool:
        """Classify transient vs permanent provider errors without relying on exact class name."""
        if isinstance(e, (TimeoutError, ConnectionError)):
            return True
        err_msg = str(e).lower()
        if "timeout" in err_msg or "connection reset" in err_msg or "broken pipe" in err_msg:
            return True

        # Check status codes
        code = getattr(e, "code", getattr(e, "status_code", None))
        if code is not None:
            if code in (429, 500, 502, 503, 504):
                return True
            if code in (400, 401, 403, 404):
                return False

        # Check google.genai error hierarchy
        if errors is not None and isinstance(e, errors.APIError):
            if isinstance(e, errors.ServerError):
                return True
            if isinstance(e, errors.ClientError):
                return code == 429
            return code in (429, 500, 502, 503, 504)

        # Catch subclasses by MRO
        mro_names = {c.__name__ for c in e.__class__.__mro__}
        if "ServerError" in mro_names:
            return True
        if "APIError" in mro_names and code in (429, 500, 502, 503, 504):
            return True

        # String clues
        if "503" in err_msg or "unavailable" in err_msg or "high demand" in err_msg or "overloaded" in err_msg:
            return True
        if "429" in err_msg or "rate limit" in err_msg or "quota" in err_msg:
            return True

        return False

    def _get_retry_after(self, e: Exception) -> float | None:
        val = getattr(e, "retry_after", None)
        if val is not None:
            try:
                return min(float(val), 10.0)
            except (ValueError, TypeError):
                pass
        headers = getattr(e, "headers", None) or getattr(getattr(e, "response", None), "headers", None)
        if isinstance(headers, dict) and "retry-after" in headers:
            try:
                return min(float(headers["retry-after"]), 10.0)
            except (ValueError, TypeError):
                pass
        return None

    def _execute_with_retry(self, operation: Callable[[], T]) -> T:
        """
        Bounded retry policy specifically at the provider adapter boundary.
        Prevents full orchestration iteration duplication and protects against cascading failures.
        """
        now = time.time()
        if self._circuit_open_until > now:
            remaining = int(self._circuit_open_until - now)
            logger.warning("Gemini circuit breaker OPEN. Cooldown active for %ds", remaining)
            raise RuntimeError(f"Gemini provider temporarily unavailable (circuit breaker open, cooldown {remaining}s)")

        max_attempts = 3
        base_delay = 0.5

        for attempt in range(1, max_attempts + 1):
            try:
                result = operation()
                # Success resets circuit breaker
                self._consecutive_failures = 0
                self._circuit_open_until = 0.0
                return result
            except Exception as e:
                is_timeout = isinstance(e, TimeoutError) or "timeout" in str(e).lower()
                retryable = self._is_transient(e)
                code = getattr(e, "code", getattr(e, "status_code", None))

                if is_timeout:
                    logger.warning(
                        "Gemini provider timeout", extra={"provider_timeout": {"elapsed_ms": 30000}}
                    )

                if not retryable or attempt == max_attempts:
                    self._consecutive_failures += 1
                    if self._consecutive_failures >= self._failure_threshold:
                        self._circuit_open_until = time.time() + self._cooldown_seconds
                        logger.error(
                            "Gemini circuit breaker tripped open after %d consecutive failures",
                            self._consecutive_failures,
                        )

                    logger.error(
                        "Gemini provider permanent failure or retry exhaustion",
                        extra={
                            "provider_failed": {
                                "failure_category": "timeout" if is_timeout else "api_error",
                                "terminal": True,
                                "code": code,
                                "exception_class": e.__class__.__name__,
                            }
                        },
                    )
                    raise RuntimeError(f"Gemini generation failed: {e}") from e

                # Check retry-after or bounded exponential backoff with jitter
                delay = self._get_retry_after(e)
                if delay is None:
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0.1, 0.4)

                logger.warning(
                    f"Transient provider error ({e.__class__.__name__} code={code}), retrying attempt {attempt}/{max_attempts} in {delay:.2f}s",
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

    def health(self) -> dict[str, Any]:
        """Observability health status of Gemini provider."""
        now = time.time()
        is_open = self._circuit_open_until > now
        has_key = bool(self.api_key)
        return {
            "provider_id": "gemini",
            "provider_name": "Google Gemini",
            "model": self.model_name,
            "has_api_key": has_key,
            "status": "circuit_open" if is_open else ("healthy" if has_key else "missing_key"),
            "consecutive_failures": self._consecutive_failures,
            "cooldown_remaining_seconds": max(0, int(self._circuit_open_until - now)) if is_open else 0,
        }

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
            if m.content and m.role != "tool":
                parts.append(types.Part.from_text(text=m.content))
                
            if m.role == "model":
                for tc in m.tool_calls:
                    p = types.Part(
                        function_call=types.FunctionCall(
                            name=tc.name, args=tc.arguments, id=tc.id
                        )
                    )
                    signature = getattr(tc, "thought_signature", None)
                    if signature is not None:
                        p.thought_signature = signature
                    parts.append(p)
                
            if m.role == "tool":
                tc_name = m.tool_calls[0].name if m.tool_calls else "tool"
                tc_id = m.tool_calls[0].id if m.tool_calls else ""
                parts.append(
                    types.Part(function_response=types.FunctionResponse(name=tc_name, id=tc_id, response={"result": m.content}))
                )
            role = "user" if m.role == "user" or m.role == "tool" else "model"
            gemini_messages.append(types.Content(role=role, parts=parts))

        gemini_tools: list[types.Tool] = []
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
            config_kwargs["automatic_function_calling"] = {"disable": True}
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
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        fc = part.function_call
                        name = fc.name or ""
                        fc_id = fc.id or name
                        args = dict(fc.args) if fc.args else {}
                        tc = ToolCall(id=fc_id, name=name, arguments=args)
                        if getattr(part, "thought_signature", None) is not None:
                            setattr(tc, "thought_signature", part.thought_signature)
                        tool_calls.append(tc)

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
