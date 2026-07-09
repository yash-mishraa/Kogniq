from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AIMetadata:
    """
    Standardized AI metadata block attached to domain entities.
    Prepares the architecture for Embeddings, Knowledge Graph integration,
    and adaptive learning signals without polluting the domain logic itself.
    """

    embedding_id: str | None = None
    kg_id: str | None = None
    mastery_score: float | None = None
    importance_score: float | None = None
    extended_attributes: dict[str, Any] = field(default_factory=dict)
