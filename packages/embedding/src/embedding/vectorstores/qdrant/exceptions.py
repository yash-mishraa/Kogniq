from embedding.vectorstores.exceptions import StoreConfigurationError, VectorStoreError


class QdrantConfigurationError(StoreConfigurationError):
    """Raised when Qdrant is improperly configured."""


class QdrantOperationError(VectorStoreError):
    """Raised when a Qdrant operation fails."""


class QdrantConnectionError(QdrantOperationError):
    """Raised when the connection to Qdrant fails."""
