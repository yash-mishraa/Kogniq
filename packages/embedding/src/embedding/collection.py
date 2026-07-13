from dataclasses import dataclass

from .embedding import Embedding
from .exceptions import InvalidEmbeddingError


@dataclass(frozen=True, slots=True)
class EmbeddingCollection:
    """A strictly validated collection of homogenous embeddings."""
    
    embeddings: tuple[Embedding, ...]
    
    def __post_init__(self) -> None:
        if not self.embeddings:
            return
            
        first_emb = self.embeddings[0]
        expected_dim = first_emb.vector.dimension
        expected_provider = first_emb.metadata.provider
        expected_model = first_emb.metadata.model_name
        
        for i, emb in enumerate(self.embeddings):
            if emb.vector.dimension != expected_dim:
                raise InvalidEmbeddingError(
                    f"Mismatched dimensions at index {i}: "
                    f"expected {expected_dim}, got {emb.vector.dimension}"
                )
            if emb.metadata.provider != expected_provider:
                raise InvalidEmbeddingError(
                    f"Mismatched provider at index {i}: "
                    f"expected '{expected_provider}', got '{emb.metadata.provider}'"
                )
            if emb.metadata.model_name != expected_model:
                raise InvalidEmbeddingError(
                    f"Mismatched model at index {i}: "
                    f"expected '{expected_model}', got '{emb.metadata.model_name}'"
                )

    @property
    def total_embeddings(self) -> int:
        return len(self.embeddings)

    @property
    def dimensions(self) -> int:
        if not self.embeddings:
            return 0
        return self.embeddings[0].vector.dimension
        
    @property
    def provider(self) -> str | None:
        if not self.embeddings:
            return None
        return self.embeddings[0].metadata.provider
