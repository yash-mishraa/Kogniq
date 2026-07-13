from abc import ABC, abstractmethod

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.vector import EmbeddingVector

from .search_result import SearchResult
from .store_info import StoreInfo


class AbstractVectorStore(ABC):
    """
    Provider-agnostic abstraction for a vector database.
    """

    @property
    @abstractmethod
    def info(self) -> StoreInfo:
        """Returns the store's configuration and capabilities."""

    @abstractmethod
    def store(self, embedding: Embedding) -> None:
        """Stores a single embedding."""

    @abstractmethod
    def store_batch(self, embeddings: EmbeddingCollection) -> None:
        """Stores a collection of embeddings."""

    @abstractmethod
    def delete(self, embedding_id: str) -> None:
        """Deletes a single embedding by its ID."""

    @abstractmethod
    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        """Deletes multiple embeddings by their IDs."""

    @abstractmethod
    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        """Searches the vector store for the closest embeddings."""

    @abstractmethod
    def count(self) -> int:
        """Returns the total number of embeddings in the store."""

    @abstractmethod
    def clear(self) -> None:
        """Removes all embeddings from the store."""
