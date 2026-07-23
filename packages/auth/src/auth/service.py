import uuid

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from .exceptions import UserAlreadyExistsError
from .interfaces import AbstractAuthenticationProvider, AbstractUserRepository
from .models import AuthenticationRequest, AuthProvider, Session, User


class AuthenticationService:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        auth_provider: AbstractAuthenticationProvider,
    ) -> None:
        self._user_repo = user_repo
        self._auth_provider = auth_provider
        self._password_hash = PasswordHash((Argon2Hasher(),))

    async def register(self, email: str, password: str, display_name: str) -> tuple[User, Session]:
        """Register a new user and automatically authenticate them."""
        if await self._user_repo.exists(email):
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        # Hash the password
        hashed_password = self._password_hash.hash(password)

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
        result = await self._auth_provider.authenticate(request)

        session = result.session
        if not session:
            session = await self._auth_provider.create_session(user.user_id)

        return user, session

    async def login(self, email: str, password: str) -> tuple[User, Session]:
        """Authenticate an existing user using credentials."""
        request = AuthenticationRequest(
            provider=AuthProvider.LOCAL,
            payload={"email": email, "password": password},
        )
        result = await self._auth_provider.authenticate(request)
        session = result.session
        if not session:
            session = await self._auth_provider.create_session(result.user.user_id)
        return result.user, session

    async def get_session(self, session_id: str) -> Session | None:
        """Validate and return an active session."""
        return await self._auth_provider.validate_session(session_id)

    async def get_user_by_session(self, session_id: str) -> User | None:
        """Return the user for an active session."""
        session = await self.get_session(session_id)
        if not session:
            return None
        return await self._user_repo.get_user(session.user_id)

    async def logout(self, session_id: str) -> None:
        """Revoke an active session."""
        await self._auth_provider.revoke_session(session_id)
