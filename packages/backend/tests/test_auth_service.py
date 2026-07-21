import pytest
from backend.services.auth_service import AuthenticationService

from auth.memory import MemoryAuthenticationProvider, MemoryUserRepository
from auth.models import AuthenticationRequest, AuthProvider, User


@pytest.fixture
def auth_service() -> AuthenticationService:
    repo = MemoryUserRepository()
    provider = MemoryAuthenticationProvider(repo)
    return AuthenticationService(auth_provider=provider, user_repository=repo)


@pytest.mark.asyncio
async def test_auth_service_orchestration(auth_service: AuthenticationService) -> None:
    # Create User
    user = User(user_id="user-1", email="test@kogniq.ai", display_name="Test")
    await auth_service.create_user(user)
    
    # Authenticate
    request = AuthenticationRequest(
        provider=AuthProvider.LOCAL,
        payload={"email": "test@kogniq.ai"}
    )
    result = await auth_service.authenticate(request)
    
    assert result.user.user_id == "user-1"
    assert result.session is not None
    
    # Get Current User
    resolved_user = await auth_service.get_current_user(result.session.session_id)
    assert resolved_user is not None
    assert resolved_user.email == "test@kogniq.ai"
    
    # Logout
    await auth_service.logout(result.session.session_id)
    
    # Session is now invalid
    resolved_user_after = await auth_service.get_current_user(result.session.session_id)
    assert resolved_user_after is None
