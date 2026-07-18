from learning_content.exceptions import LearningContentError


class GenerationProviderError(LearningContentError):
    """Base exception for all text generation provider errors."""


class OpenRouterError(GenerationProviderError):
    """Base exception for OpenRouter specific errors."""


class OpenRouterAuthenticationError(OpenRouterError):
    """Raised when authentication with OpenRouter fails."""


class OpenRouterRateLimitError(OpenRouterError):
    """Raised when OpenRouter rate limits are exceeded."""


class OpenRouterConnectionError(OpenRouterError):
    """Raised when the connection to OpenRouter fails."""


class OpenRouterResponseError(OpenRouterError):
    """Raised when OpenRouter returns an unexpected or invalid response."""
