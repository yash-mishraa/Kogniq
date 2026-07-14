from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from knowledge.extractors.registry_exceptions import (
    DuplicateExtractorError,
    ExtractorNotFoundError,
)


class KnowledgeExtractorRegistry:
    """Registry for managing and resolving Knowledge Extractors by ID."""

    def __init__(self) -> None:
        self._extractors: dict[str, AbstractKnowledgeExtractor] = {}

    def register(self, extractor: AbstractKnowledgeExtractor) -> None:
        """Register a new extractor."""
        extractor_id = extractor.info.extractor_id
        if extractor_id in self._extractors:
            raise DuplicateExtractorError(f"Extractor '{extractor_id}' is already registered.")
        self._extractors[extractor_id] = extractor

    def extractor(self, extractor_id: str) -> AbstractKnowledgeExtractor:
        """Retrieve an extractor by ID."""
        if extractor_id not in self._extractors:
            raise ExtractorNotFoundError(f"Extractor '{extractor_id}' is not registered.")
        return self._extractors[extractor_id]

    def has_extractor(self, extractor_id: str) -> bool:
        """Check if an extractor is registered."""
        return extractor_id in self._extractors

    def available_extractors(self) -> tuple[str, ...]:
        """Get a tuple of all registered extractor IDs."""
        return tuple(self._extractors.keys())

    @property
    def extractor_count(self) -> int:
        """Get the total number of registered extractors."""
        return len(self._extractors)
