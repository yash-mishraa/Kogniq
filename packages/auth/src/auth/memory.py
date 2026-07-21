import threading
import uuid
from datetime import UTC, datetime, timedelta

from .interfaces import AbstractAuthenticationProvider, AbstractUserRepository
from .models import (
    AuthenticationRequest,
    AuthenticationResult,
    Identity,
    Session,
    User,
)


class MemoryUserRepository(AbstractUserRepository):
    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._lock = threading.RLock()

    async def create_user(self, user: User) -> User:
        with self._lock:
            if await self.exists(user.email):
                raise ValueError(f"User with email {user.email} already exists")
            self._users[user.user_id] = user
            return user

    async def get_user(self, user_id: str) -> User | None:
        with self._lock:
            return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        with self._lock:
            for user in self._users.values():
                if user.email == email:
                    return user
            return None

    async def update_user(self, user: User) -> User:
        with self._lock:
            if user.user_id not in self._users:
                raise ValueError(f"User with id {user.user_id} not found")
            self._users[user.user_id] = user
            return user

    async def delete_user(self, user_id: str) -> None:
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]

    async def list_users(self) -> list[User]:
        with self._lock:
            return list(self._users.values())

    async def exists(self, email: str) -> bool:
        with self._lock:
            return any(user.email == email for user in self._users.values())


class MemoryAuthenticationProvider(AbstractAuthenticationProvider):
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._user_repo = user_repo
        self._sessions: dict[str, Session] = {}
        self._identities: dict[str, list[Identity]] = {}
        self._lock = threading.RLock()

    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """Simulate authentication without checking actual passwords."""
        email = request.payload.get("email")
        if not email:
            raise ValueError("Email is required for local authentication")

        user = await self._user_repo.get_user_by_email(email)
        if not user:
            raise ValueError("Authentication failed: User not found")
            
        with self._lock:
            # Upsert Identity
            user_identities = self._identities.setdefault(user.user_id, [])
            provider_user_id = request.payload.get("provider_user_id", email)
            
            identity = None
            for idx in user_identities:
                if idx.provider == request.provider and idx.provider_user_id == provider_user_id:
                    identity = idx
                    break
                    
            if not identity:
                identity = Identity(
                    identity_id=str(uuid.uuid4()),
                    user_id=user.user_id,
                    provider=request.provider,
                    provider_user_id=provider_user_id
                )
                user_identities.append(identity)

        session = await self.create_session(user.user_id)

        return AuthenticationResult(
            user=user,
            identity=identity,
            provider=request.provider,
            session=session,
            authenticated_at=datetime.now(UTC)
        )

    async def create_session(self, user_id: str) -> Session:
        with self._lock:
            session_id = str(uuid.uuid4())
            # Default session expiration of 24 hours
            expires_at = datetime.now(UTC) + timedelta(hours=24)
            session = Session(session_id=session_id, user_id=user_id, expires_at=expires_at)
            self._sessions[session_id] = session
            return session

    async def validate_session(self, session_id: str) -> Session | None:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            if not session.is_active:
                return None
            if session.expires_at < datetime.now(UTC):
                # Mark expired
                self._sessions[session_id] = Session(
                    session_id=session.session_id,
                    user_id=session.user_id,
                    expires_at=session.expires_at,
                    is_active=False,
                    created_at=session.created_at
                )
                return None
            return session

    async def revoke_session(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session and session.is_active:
                self._sessions[session_id] = Session(
                    session_id=session.session_id,
                    user_id=session.user_id,
                    expires_at=session.expires_at,
                    is_active=False,
                    created_at=session.created_at
                )
