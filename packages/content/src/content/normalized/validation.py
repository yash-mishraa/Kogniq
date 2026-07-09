from ..domain.domain_errors import ContentDomainError


class NormalizedDocumentError(ContentDomainError):
    """Base exception for normalized document validation failures."""


class InvalidDocumentError(NormalizedDocumentError):
    """Raised when document-level validation fails."""


class InvalidPageError(NormalizedDocumentError):
    """Raised when page-level validation fails."""


class InvalidBlockError(NormalizedDocumentError):
    """Raised when block-level validation fails."""


def validate_not_empty(
    value: str,
    field_name: str,
    exception_class: type[NormalizedDocumentError] = InvalidDocumentError,
) -> None:
    """Validates that a string is not empty or entirely whitespace."""
    if not value or not value.strip():
        raise exception_class(f"{field_name} cannot be empty.")


def validate_positive(
    value: int | float,
    field_name: str,
    exception_class: type[NormalizedDocumentError] = InvalidDocumentError,
) -> None:
    """Validates that a number is strictly positive."""
    if value <= 0:
        raise exception_class(f"{field_name} must be positive, got {value}.")


def validate_non_negative(
    value: int | float,
    field_name: str,
    exception_class: type[NormalizedDocumentError] = InvalidDocumentError,
) -> None:
    """Validates that a number is non-negative."""
    if value < 0:
        raise exception_class(f"{field_name} cannot be negative, got {value}.")
