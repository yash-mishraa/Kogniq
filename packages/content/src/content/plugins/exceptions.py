from ..domain.domain_errors import ContentDomainError


class ContentPluginError(ContentDomainError):
    """Base exception for all content plugin errors."""


class DuplicateProcessorError(ContentPluginError):
    """Raised when attempting to register a processor that conflicts with an existing one
    (name, extension, or mime type)."""


class ProcessorNotFoundError(ContentPluginError):
    """Raised when a requested processor cannot be found."""


class InvalidProcessorError(ContentPluginError):
    """Raised when a processor does not meet the required interface or contract."""
