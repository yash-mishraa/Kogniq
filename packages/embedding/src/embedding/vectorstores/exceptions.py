class VectorStoreError(Exception):
    """Base exception for all Vector Store errors."""

class StoreConfigurationError(VectorStoreError):
    """Raised when a store is improperly configured."""

class StoreCapabilityError(VectorStoreError):
    """Raised when a requested operation is not supported by the store."""

class BatchLimitExceededError(VectorStoreError):
    """Raised when an operation exceeds the store's maximum batch size."""

class StorageError(VectorStoreError):
    """Raised when inserting/storing embeddings fails."""

class SearchError(VectorStoreError):
    """Raised when querying the vector store fails."""

class DeletionError(VectorStoreError):
    """Raised when deleting embeddings fails."""
