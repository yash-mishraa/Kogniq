from backend.dependencies import get_register_user_use_case
from fastapi import APIRouter, Depends, Response

from application.auth.register_user import RegisterUserCommand, RegisterUserUseCase
from apps.api.app.core.auth.cookie import SessionCookieHandler
from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.auth import (
    AuthServiceDependency,
    CurrentUserDependency,
    SessionDependency,
)
from apps.api.app.dependencies.request import SettingsDependency
from apps.api.app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from auth.exceptions import (
    AuthDomainError,
    InvalidCredentialsError,
    SessionExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

router = APIRouter(tags=["authentication"])


def _map_auth_error(e: AuthDomainError) -> APIError:
    if isinstance(e, UserAlreadyExistsError):
        return APIError(
            status_code=409,
            code="user_already_exists",
            message=str(e),
        )
    elif isinstance(e, InvalidCredentialsError):
        return APIError(
            status_code=400,
            code="invalid_credentials",
            message=str(e),
        )
    elif isinstance(e, UserNotFoundError):
        return APIError(
            status_code=401,
            code="user_not_found",
            message=str(e),
        )
    elif isinstance(e, SessionExpiredError):
        return APIError(
            status_code=401,
            code="session_expired",
            message=str(e),
        )
    return APIError(
        status_code=500,
        code="auth_error",
        message=str(e),
    )





@router.post("/auth/register", response_model=UserResponse)
async def register_user(
    request_data: RegisterRequest,
    response: Response,
    settings: SettingsDependency,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case), # noqa: B008
) -> UserResponse:
    """Create a new account, assign default roles, and establish an authenticated session."""
    try:
        command = RegisterUserCommand(
            email=request_data.email,
            password=request_data.password,
            display_name=request_data.display_name,
        )
        result = await use_case.execute(command)
    except AuthDomainError as e:
        raise _map_auth_error(e) from e

    cookie_handler = SessionCookieHandler(settings)
    cookie_handler.set_session_cookie(response, result.session.session_id)
    return UserResponse.model_validate(result.user)


@router.post("/auth/login", response_model=UserResponse)
async def login_user(
    request_data: LoginRequest,
    response: Response,
    auth_service: AuthServiceDependency,
    settings: SettingsDependency,
) -> UserResponse:
    """Authenticate and establish a new session."""
    try:
        user, session = await auth_service.login(
            email=request_data.email,
            password=request_data.password,
        )
    except AuthDomainError as e:
        raise _map_auth_error(e) from e

    cookie_handler = SessionCookieHandler(settings)
    cookie_handler.set_session_cookie(response, session.session_id)
    return UserResponse.model_validate(user)


@router.get("/auth/session", response_model=UserResponse)
async def get_session_user(
    current_user: CurrentUserDependency,
) -> UserResponse:
    """Return the user for the currently active session."""
    return UserResponse.model_validate(current_user)


@router.post("/auth/logout")
async def logout_user(
    session: SessionDependency,
    response: Response,
    auth_service: AuthServiceDependency,
    settings: SettingsDependency,
) -> dict[str, str]:
    """Revoke the current session and clear the session cookie."""
    await auth_service.logout(session.session_id)
    cookie_handler = SessionCookieHandler(settings)
    cookie_handler.clear_session_cookie(response)
    return {"status": "success"}


@router.get("/auth/csrf")
async def get_csrf_token() -> dict[str, str]:
    """Reserved endpoint for future CSRF protection."""
    return {"message": "CSRF protection reserved for future implementation"}
