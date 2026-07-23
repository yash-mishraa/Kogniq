from shared.exceptions import KogniqError


class AuthDomainError(KogniqError):
    """Base exception for all auth domain errors."""


class UserAlreadyExistsError(AuthDomainError):
    """Raised when attempting to register with an email that is already registered."""


class InvalidCredentialsError(AuthDomainError):
    """Raised when authentication fails due to invalid credentials."""


class UserNotFoundError(AuthDomainError):
    """Raised when a user is not found."""


class SessionExpiredError(AuthDomainError):
    """Raised when a session has expired or is invalid."""
