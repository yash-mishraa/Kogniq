from ..domain.domain_errors import ContentDomainError


class ContentPluginError(ContentDomainError):
    """Base exception for all content plugin errors."""


class DuplicateProcessorError(ContentPluginError):
    """Raised when attempting to register a processor that conflicts with an existing name."""


class DuplicateExtensionError(ContentPluginError):
    """Raised when attempting to register a processor with an extension already registered."""


class DuplicateMimeTypeError(ContentPluginError):
    """Raised when attempting to register a processor with a MIME type already registered."""


class ProcessorNotFoundError(ContentPluginError):
    """Raised when a requested processor cannot be found."""


class InvalidProcessorDefinitionError(ContentPluginError):
    """Raised when a processor does not meet the required interface or has invalid info."""


class UnsupportedResourceError(ContentPluginError):
    """Raised when a resource's extension or MIME type is not supported by any processor."""
