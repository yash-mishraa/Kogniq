from auth.interfaces import AbstractAuthenticationProvider, AbstractUserRepository
from auth.models import AuthenticationRequest, AuthenticationResult, Session, User


class AuthenticationService:
    def __init__(
        self,
        auth_provider: AbstractAuthenticationProvider,
        user_repository: AbstractUserRepository,
    ) -> None:
        self._provider = auth_provider
        self._user_repo = user_repository

    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """Authenticate a user using the underlying provider."""
        return await self._provider.authenticate(request)

    async def create_user(self, user: User) -> User:
        """Create a new user in the system."""
        return await self._user_repo.create_user(user)

    async def get_current_user(self, session_id: str) -> User | None:
        """Resolve the currently authenticated user from a session."""
        session = await self.validate_session(session_id)
        if not session:
            return None
        return await self._user_repo.get_user(session.user_id)

    async def validate_session(self, session_id: str) -> Session | None:
        """Validate a session via the provider."""
        return await self._provider.validate_session(session_id)

    async def logout(self, session_id: str) -> None:
        """Revoke a session (logout)."""
        await self._provider.revoke_session(session_id)
