from ..domain.domain_errors import ContentDomainError


class ChunkEngineError(ContentDomainError):
    """Base exception for chunk engine domain failures."""

class InvalidChunkError(ChunkEngineError):
    """Raised when chunk-level validation fails."""

class InvalidChunkCollectionError(ChunkEngineError):
    """Raised when chunk collection validation fails."""
