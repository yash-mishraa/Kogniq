from ...domain.domain_errors import ContentDomainError


class DOCXProcessorError(ContentDomainError):
    """Base exception for DOCX processor errors."""


class DOCXEmptyError(DOCXProcessorError):
    """Raised when the DOCX document is empty."""


class DOCXCorruptedError(DOCXProcessorError):
    """Raised when the DOCX file is corrupted or not a valid ZIP package."""


class DOCXUnsupportedError(DOCXProcessorError):
    """Raised when the DOCX file contains unsupported structures."""
