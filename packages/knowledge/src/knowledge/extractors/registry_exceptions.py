from knowledge.extractors.exceptions import KnowledgeExtractionError


class DuplicateExtractorError(KnowledgeExtractionError):
    """Raised when attempting to register an extractor with an ID that already exists."""


class ExtractorNotFoundError(KnowledgeExtractionError):
    """Raised when requesting an extractor ID that is not registered."""


class InvalidExtractorDefinitionError(KnowledgeExtractionError):
    """Raised when an extractor fails registration validation."""
