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

    async def register(self, email: str, password: str, display_name: str) -> tuple[User, Session]:
        """Register a new user and authenticate."""
        import uuid

        from pwdlib import PasswordHash
        from pwdlib.hashers.argon2 import Argon2Hasher

        from auth.exceptions import UserAlreadyExistsError
        from auth.models import AuthProvider

        if await self._user_repo.exists(email):
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        # Hash the password
        password_hash = PasswordHash((Argon2Hasher(),))
        hashed_password = password_hash.hash(password)

        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            email=email,
            display_name=display_name,
        )

        user = await self._user_repo.create_user(user)

        # The memory implementation is adapted to handle password setting
        if hasattr(self._user_repo, "set_password_hash"):
            await self._user_repo.set_password_hash(user.user_id, hashed_password)

        # Authenticate immediately
        request = AuthenticationRequest(
            provider=AuthProvider.LOCAL,
            payload={"email": email, "password": password, "is_registration": True},
        )
        result = await self._provider.authenticate(request)

        session = result.session
        if not session:
            session = await self._provider.create_session(user.user_id)

        return user, session

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
