class EducationDomainError(Exception):
    """Base exception for all educational knowledge layer failures."""


class InvalidConceptError(EducationDomainError):
    """Raised when a concept or its associated entities fail validation."""


class InvalidRelationshipError(EducationDomainError):
    """Raised when a relationship fails validation."""


def validate_not_empty(
    value: str, field_name: str, exception_class: type[EducationDomainError] = InvalidConceptError
) -> None:
    if not value or not value.strip():
        raise exception_class(f"{field_name} cannot be empty.")
