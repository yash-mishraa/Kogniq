from dataclasses import dataclass

from knowledge.exceptions import KnowledgeDomainError


@dataclass(frozen=True, kw_only=True)
class KnowledgeMetadata:
    """Immutable metadata describing the origin and confidence of a knowledge entity."""

    source_document: str
    source_chunk: str
    language: str
    confidence: float
    extraction_version: str
    created_by: str

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise KnowledgeDomainError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
