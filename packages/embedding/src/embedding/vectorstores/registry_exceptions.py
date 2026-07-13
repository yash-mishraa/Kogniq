from .exceptions import VectorStoreError


class DuplicateStoreError(VectorStoreError):
    """Raised when attempting to register a store_id that already exists."""

class StoreNotFoundError(VectorStoreError):
    """Raised when querying a store_id that does not exist."""

class InvalidStoreDefinitionError(VectorStoreError):
    """Raised when a registered object does not implement AbstractVectorStore."""
