"""Authentication domain package."""

from .exceptions import (
    AuthDomainError,
    InvalidCredentialsError,
    SessionExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from .interfaces import AbstractAuthenticationProvider, AbstractUserRepository
from .memory import MemoryAuthenticationProvider, MemoryUserRepository
from .models import (
    AuthenticationRequest,
    AuthenticationResult,
    AuthProvider,
    Identity,
    Session,
    User,
)
from .service import AuthenticationService

__all__ = [
    "AbstractAuthenticationProvider",
    "AbstractUserRepository",
    "AuthDomainError",
    "AuthProvider",
    "AuthenticationRequest",
    "AuthenticationResult",
    "AuthenticationService",
    "Identity",
    "InvalidCredentialsError",
    "MemoryAuthenticationProvider",
    "MemoryUserRepository",
    "Session",
    "SessionExpiredError",
    "User",
    "UserAlreadyExistsError",
    "UserNotFoundError",
]
