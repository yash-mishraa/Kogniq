from dataclasses import dataclass

from application.exceptions import ApplicationError
from application.interfaces import AuthenticationServiceProtocol, AuthorizationServiceProtocol
from auth.models import Session, User


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str
    display_name: str


@dataclass(frozen=True)
class RegisterUserResult:
    user: User
    session: Session


class RegisterUserUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        authorization_service: AuthorizationServiceProtocol,
    ) -> None:
        self._auth_service = auth_service
        self._authorization_service = authorization_service

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:

        # 1. Create user and session
        try:
            user, session = await self._auth_service.register(
                email=command.email,
                password=command.password,
                display_name=command.display_name,
            )
        except Exception as e:
            # We catch exceptions to map domain errors in the router,
            # but let AuthDomainErrors bubble up
            raise e

        # 2. Assign default role
        try:
            # ROLE_USER_ID is defined as "USER" in backend.security.policies
            # But the use case shouldn't directly import from backend.
            # We can use the string literal, or inject it via config.
            await self._authorization_service.assign_role(user.user_id, "USER")
        except Exception as e:
            # If role assignment fails, we shouldn't necessarily fail registration,
            # or maybe we should?
            # It's better to raise it so the client knows it failed.
            raise ApplicationError(f"Failed to assign default role: {e}") from e

        return RegisterUserResult(user=user, session=session)
