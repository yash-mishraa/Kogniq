from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)
from learning_content.providers.openrouter.client import LazyOpenRouterClient
from learning_content.providers.openrouter.exceptions import OpenRouterError


class OpenRouterTextGenerationProvider(AbstractTextGenerationProvider):
    """
    Concrete implementation of a text generation provider using OpenRouter.
    """

    def __init__(
        self, api_key: str, model_name: str, base_url: str = "https://openrouter.ai/api/v1"
    ) -> None:
        """
        Initialize the provider with configuration.
        """
        self._model_name = model_name
        self._client = LazyOpenRouterClient(api_key=api_key, base_url=base_url)

        self._info = TextGenerationProviderInfo(
            provider_id="openrouter",
            provider_name="OpenRouter API",
            default_model=model_name,
            model_version="latest",
            context_window=128000,  # Generic safe default, actual depends on model
            supports_streaming=True,
            supports_json=True,
            supports_images=False,
            supports_tools=True,
        )

    @property
    def info(self) -> TextGenerationProviderInfo:
        """Get the capability metadata for OpenRouter."""
        return self._info

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text using the OpenRouter client.

        Args:
            prompt: The full prompt string.
            temperature: Optional generation temperature.
            max_tokens: Optional maximum tokens to generate.

        Returns:
            The raw text response.

        Raises:
            OpenRouterError: If validation or generation fails.
        """
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise OpenRouterError("Prompt cannot be empty or whitespace only.")

        return self._client.generate(
            prompt=cleaned_prompt,
            model=self._model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
