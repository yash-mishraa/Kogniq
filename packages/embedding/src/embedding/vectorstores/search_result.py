from dataclasses import dataclass

from embedding.embedding import Embedding


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Represents a matched embedding retrieved from a Vector Store."""

    embedding: Embedding
    similarity_score: float
