from embedding.exceptions import EmbeddingDomainError


class EmbeddingProviderError(EmbeddingDomainError):
    """Base exception for all errors within the embedding provider abstraction."""


class ProviderConfigurationError(EmbeddingProviderError):
    """Raised when a ProviderInfo instance violates required invariants."""


class ProviderCapabilityError(EmbeddingProviderError):
    """Raised when a caller attempts an operation the provider doesn't support."""


class BatchLimitExceededError(EmbeddingProviderError):
    """Raised when a requested batch size exceeds the provider's limits."""


class EmbeddingGenerationError(EmbeddingProviderError):
    """Raised when the underlying AI provider fails to generate an embedding."""
