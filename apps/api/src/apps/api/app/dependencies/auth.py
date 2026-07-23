from typing import Annotated

from fastapi import Depends, Request

from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.request import SettingsDependency
from auth import (
    AuthenticationService,
    MemoryAuthenticationProvider,
    MemoryUserRepository,
    Session,
    User,
)

# Global singletons for memory provider during development
_memory_user_repo = MemoryUserRepository()
_memory_auth_provider = MemoryAuthenticationProvider(_memory_user_repo)


def get_auth_service() -> AuthenticationService:
    return AuthenticationService(_memory_user_repo, _memory_auth_provider)


AuthServiceDependency = Annotated[AuthenticationService, Depends(get_auth_service)]


async def get_current_session(
    request: Request,
    settings: SettingsDependency,
    auth_service: AuthServiceDependency,
) -> Session:
    """Retrieve and validate the active session from the session cookie."""
    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        raise APIError(
            status_code=401,
            code="missing_session",
            message="No active session found. Please sign in.",
        )

    session = await auth_service.get_session(session_id)
    if not session:
        # We also instruct the client to clear the invalid cookie.
        # This will be handled by raising APIError and potentially appending clear cookie headers,
        # but for now we just raise the error and let the frontend clear on 401.
        raise APIError(
            status_code=401,
            code="invalid_session",
            message="Your session has expired. Please sign in to continue.",
        )

    return session


SessionDependency = Annotated[Session, Depends(get_current_session)]


async def get_current_user(
    session: SessionDependency,
    auth_service: AuthServiceDependency,
) -> User:
    """Retrieve the user associated with the active session."""
    user = await auth_service.get_user_by_session(session.session_id)
    if not user:
        raise APIError(
            status_code=401,
            code="user_not_found",
            message="The user associated with this session no longer exists.",
        )
    return user


CurrentUserDependency = Annotated[User, Depends(get_current_user)]
