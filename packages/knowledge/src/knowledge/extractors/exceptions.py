from knowledge.exceptions import KnowledgeDomainError


class KnowledgeExtractionError(KnowledgeDomainError):
    """Base exception for all knowledge extraction errors."""


class ExtractorConfigurationError(KnowledgeExtractionError):
    """Raised when an extractor is improperly configured."""


class ExtractorCapabilityError(KnowledgeExtractionError):
    """Raised when an extractor is asked to perform an unsupported operation."""


class BatchLimitExceededError(KnowledgeExtractionError):
    """Raised when a batch size exceeds the extractor's maximum limits."""
