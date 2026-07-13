from ...domain.domain_errors import ContentDomainError


class TXTProcessorError(ContentDomainError):
    """Base exception for TXT processor errors."""

class TXTEmptyError(TXTProcessorError):
    """Raised when the TXT document is empty or only contains whitespace."""

class TXTUnsupportedEncodingError(TXTProcessorError):
    """Raised when the TXT file contains an unsupported encoding."""

class TXTInvalidStreamError(TXTProcessorError):
    """Raised when the TXT stream cannot be processed."""
