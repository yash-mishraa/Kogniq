from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class TextGenerationProviderInfo:
    """Metadata about a text generation provider's capabilities."""

    provider_id: str
    provider_name: str
    default_model: str
    context_window: int
    supports_streaming: bool = False
    supports_json: bool = False
    supports_images: bool = False
    supports_tools: bool = False


class AbstractTextGenerationProvider(ABC):
    """
    Abstract interface for text generation providers.

    This provider is purely for text generation and should not contain any
    business logic, prompt construction, or response parsing. It serves as
    a generic, reusable interface for all learning generators.
    """

    @property
    @abstractmethod
    def info(self) -> TextGenerationProviderInfo:
        """Get the immutable capability metadata for this provider."""
        ...

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text from a given prompt.

        Args:
            prompt: The complete string prompt.
            temperature: Optional generation temperature (0.0 to 2.0).
            max_tokens: Optional maximum number of tokens to generate.

        Returns:
            The raw generated text.
        """
        ...

    def generate_batch(
        self,
        prompts: tuple[str, ...],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[str, ...]:
        """
        Generate text for multiple prompts.

        Default implementation calls generate() sequentially. Providers may
        override this if they support native batching or parallel execution.
        """
        return tuple(
            self.generate(prompt, temperature=temperature, max_tokens=max_tokens)
            for prompt in prompts
        )
