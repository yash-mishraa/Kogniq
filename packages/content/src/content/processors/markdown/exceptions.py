from ...domain.domain_errors import ContentDomainError


class MarkdownProcessorError(ContentDomainError):
    """Base exception for Markdown processor errors."""


class MarkdownEmptyError(MarkdownProcessorError):
    """Raised when the Markdown document is empty or contains no valid blocks."""


class MarkdownEncodingError(MarkdownProcessorError):
    """Raised when the Markdown byte stream cannot be decoded."""


class MarkdownMalformedError(MarkdownProcessorError):
    """Raised when the Markdown parsing fails catastrophically."""
