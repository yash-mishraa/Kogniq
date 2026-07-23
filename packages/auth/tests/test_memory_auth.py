import uuid
from datetime import UTC, datetime, timedelta

import pytest

from auth.exceptions import UserAlreadyExistsError, UserNotFoundError
from auth.memory import MemoryAuthenticationProvider, MemoryUserRepository
from auth.models import (
    AuthenticationRequest,
    AuthProvider,
    User,
)


@pytest.fixture
def repo() -> MemoryUserRepository:
    return MemoryUserRepository()


@pytest.fixture
def provider(repo: MemoryUserRepository) -> MemoryAuthenticationProvider:
    return MemoryAuthenticationProvider(repo)


@pytest.mark.asyncio
async def test_create_and_get_user(repo: MemoryUserRepository) -> None:
    user = User(user_id="user-1", email="test@kogniq.ai", display_name="Test User")

    created = await repo.create_user(user)
    assert created.user_id == "user-1"

    fetched = await repo.get_user("user-1")
    assert fetched is not None
    assert fetched.email == "test@kogniq.ai"


@pytest.mark.asyncio
async def test_create_duplicate_user(repo: MemoryUserRepository) -> None:
    user1 = User(user_id="user-1", email="test@kogniq.ai", display_name="Test User 1")
    user2 = User(user_id="user-2", email="test@kogniq.ai", display_name="Test User 2")

    await repo.create_user(user1)

    with pytest.raises(UserAlreadyExistsError, match="already exists"):
        await repo.create_user(user2)


@pytest.mark.asyncio
async def test_authentication_flow(
    repo: MemoryUserRepository,
    provider: MemoryAuthenticationProvider,
) -> None:
    # 1. Setup user
    user = User(user_id="user-1", email="test@kogniq.ai", display_name="Test User")
    await repo.create_user(user)

    # 2. Authenticate
    request = AuthenticationRequest(
        provider=AuthProvider.LOCAL, payload={"email": "test@kogniq.ai"}
    )
    result = await provider.authenticate(request)

    assert result.user.user_id == "user-1"
    assert result.identity.provider == AuthProvider.LOCAL
    assert result.identity.provider_user_id == "test@kogniq.ai"
    assert result.session is not None
    assert result.session.is_active is True

    # 3. Validate Session
    session = await provider.validate_session(result.session.session_id)
    assert session is not None
    assert session.is_active is True

    # 4. Revoke Session
    await provider.revoke_session(result.session.session_id)
    session_after = await provider.validate_session(result.session.session_id)
    assert session_after is None


@pytest.mark.asyncio
async def test_authentication_missing_user(provider: MemoryAuthenticationProvider) -> None:
    request = AuthenticationRequest(
        provider=AuthProvider.LOCAL, payload={"email": "unknown@kogniq.ai"}
    )
    with pytest.raises(UserNotFoundError, match="User not found"):
        await provider.authenticate(request)


@pytest.mark.asyncio
async def test_multiple_identities(
    repo: MemoryUserRepository,
    provider: MemoryAuthenticationProvider,
) -> None:
    user = User(user_id="user-1", email="test@kogniq.ai", display_name="Test User")
    await repo.create_user(user)

    # Login via Local
    res1 = await provider.authenticate(
        AuthenticationRequest(provider=AuthProvider.LOCAL, payload={"email": "test@kogniq.ai"})
    )

    # Login via Google
    res2 = await provider.authenticate(
        AuthenticationRequest(
            provider=AuthProvider.GOOGLE,
            payload={"email": "test@kogniq.ai", "provider_user_id": "google_123"},
        )
    )

    assert res1.identity.provider == AuthProvider.LOCAL
    assert res2.identity.provider == AuthProvider.GOOGLE

    # Identity ID should differ
    assert res1.identity.identity_id != res2.identity.identity_id
    # Both map to same user
    assert res1.user.user_id == res2.user.user_id


@pytest.mark.asyncio
async def test_expired_session(provider: MemoryAuthenticationProvider) -> None:
    # Create fake expired session
    session_id = str(uuid.uuid4())
    from auth.models import Session

    provider._sessions[session_id] = Session(
        session_id=session_id, user_id="user-1", expires_at=datetime.now(UTC) - timedelta(hours=1)
    )

    # Validate
    res = await provider.validate_session(session_id)
    assert res is None

    # Verify it was marked inactive
    assert provider._sessions[session_id].is_active is False
