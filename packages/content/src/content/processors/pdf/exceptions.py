from ...domain.domain_errors import ContentDomainError


class PDFProcessorError(ContentDomainError):
    """Base exception for PDF processor errors."""


class PDFCorruptedError(PDFProcessorError):
    """Raised when PDF is corrupted or cannot be opened."""


class PDFEncryptedError(PDFProcessorError):
    """Raised when PDF is encrypted and requires a password."""


class PDFUnsupportedError(PDFProcessorError):
    """Raised when PDF format or features are unsupported."""


class PDFEmptyError(PDFProcessorError):
    """Raised when PDF contains zero pages."""
