from .exceptions import EmbeddingProviderError


class DuplicateProviderError(EmbeddingProviderError):
    """Raised when attempting to register a provider ID that already exists."""


class ProviderNotFoundError(EmbeddingProviderError):
    """Raised when looking up a provider ID that does not exist."""


class InvalidProviderDefinitionError(EmbeddingProviderError):
    """Raised when a registered object does not implement AbstractEmbeddingProvider."""
