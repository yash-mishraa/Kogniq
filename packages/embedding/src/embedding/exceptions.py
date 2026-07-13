class EmbeddingDomainError(Exception):
    """Base exception for all errors within the embedding domain."""

class InvalidEmbeddingError(EmbeddingDomainError):
    """Raised when an embedding or collection violates consistency invariants."""

class InvalidVectorDimensionError(EmbeddingDomainError):
    """Raised when a vector has zero, negative, or mismatched dimensions."""

class EmbeddingProviderError(EmbeddingDomainError):
    """Raised when provider execution fails or metadata mismatches."""
