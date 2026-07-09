from ..domain.domain_errors import ContentDomainError


class ResourceError(ContentDomainError):
    """Base exception for all resource handle failures."""


class InvalidResourceHandleError(ResourceError):
    """Raised when resource handle validation fails (e.g. empty filename, negative size)."""


class InvalidChecksumError(ResourceError):
    """Raised when checksum validation fails."""


def validate_not_empty(
    value: str, field_name: str, exception_class: type[ResourceError] = InvalidResourceHandleError
) -> None:
    """Validates that a string is not empty or entirely whitespace."""
    if not value or not value.strip():
        raise exception_class(f"{field_name} cannot be empty.")


def validate_non_negative(
    value: int | float,
    field_name: str,
    exception_class: type[ResourceError] = InvalidResourceHandleError,
) -> None:
    """Validates that a number is non-negative."""
    if value < 0:
        raise exception_class(f"{field_name} cannot be negative, got {value}.")
