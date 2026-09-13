import logging

from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
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
        model_name: str = "gemini-2.0-flash",
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
            model_version="2.0",
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
