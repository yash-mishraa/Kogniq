class ChromaError(Exception):
    """Base class for internal ChromaDB errors before wrapping."""


class ChromaInitializationError(ChromaError):
    """Raised when Chroma client fails to initialize."""


class ChromaOperationError(ChromaError):
    """Raised when a Chroma operation (insert/search/delete) fails."""
