from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalCommand:
    user_id: str
    query: str
    document_id: str | None = None
    top_k: int = 5
    minimum_similarity: float | None = None
