from abc import ABC, abstractmethod

from content.chunking import Chunk, ChunkCollection
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding

from .provider_info import ProviderInfo


class AbstractEmbeddingProvider(ABC):
    """
    The canonical abstraction layer for all AI embedding providers.
    Concrete implementations (e.g., OpenAI, Gemini, Local) must implement
    this interface without leaking HTTP or SDK details to the caller.
    """
    
    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        """Return the immutable metadata characterizing this provider."""
        
    @abstractmethod
    def generate(self, chunk: Chunk) -> Embedding:
        """
        Transform a single chunk into an Embedding.
        
        Raises:
            EmbeddingGenerationError: If the provider fails to generate.
        """
        
    @abstractmethod
    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        """
        Transform a batch of chunks into an EmbeddingCollection.
        
        Raises:
            BatchLimitExceededError: If len(chunks) > info.maximum_batch_size.
            ProviderCapabilityError: If the provider doesn't support batch generation.
            EmbeddingGenerationError: If the provider fails to generate.
        """
