from abc import ABC, abstractmethod

from .models import AuthenticationRequest, AuthenticationResult, Session, User


class AbstractAuthenticationProvider(ABC):
    @abstractmethod
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """Authenticate a user and return the result."""

    @abstractmethod
    async def create_session(self, user_id: str) -> Session:
        """Create a new session for a user."""

    @abstractmethod
    async def validate_session(self, session_id: str) -> Session | None:
        """Validate an existing session."""

    @abstractmethod
    async def revoke_session(self, session_id: str) -> None:
        """Revoke a session (mark as inactive)."""


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user."""

    @abstractmethod
    async def get_user(self, user_id: str) -> User | None:
        """Get a user by ID."""

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email."""

    @abstractmethod
    async def update_user(self, user: User) -> User:
        """Update an existing user."""

    @abstractmethod
    async def delete_user(self, user_id: str) -> None:
        """Delete a user."""

    @abstractmethod
    async def list_users(self) -> list[User]:
        """List all users."""

    @abstractmethod
    async def exists(self, email: str) -> bool:
        """Check if a user exists by email."""
