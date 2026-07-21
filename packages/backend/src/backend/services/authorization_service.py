from collections.abc import Sequence

from backend.core.exceptions import BackendError

from auth.authorization import AuthorizationResult, Permission, Role
from auth.authorization_interfaces import (
    AbstractAuthorizationProvider,
    AbstractPermissionRepository,
    AbstractRoleRepository,
)


class AuthorizationError(BackendError):
    """Raised when authorization is denied."""

    def __init__(self, message: str) -> None:
        super().__init__(code="AUTHORIZATION_DENIED", message=message, status_code=403)


class AuthorizationService:
    def __init__(
        self,
        auth_provider: AbstractAuthorizationProvider,
        role_repo: AbstractRoleRepository,
        permission_repo: AbstractPermissionRepository,
    ) -> None:
        self._auth_provider = auth_provider
        self._role_repo = role_repo
        self._permission_repo = permission_repo

    async def assign_role(self, user_id: str, role_id: str) -> None:
        await self._auth_provider.assign_role(user_id, role_id)

    async def remove_role(self, user_id: str, role_id: str) -> None:
        await self._auth_provider.remove_role(user_id, role_id)

    async def require_permission(self, user_id: str, permission_id: str) -> AuthorizationResult:
        result = await self._auth_provider.has_permission(user_id, permission_id)
        if not result.allowed:
            raise AuthorizationError(f"Permission denied: {result.reason}")
        return result

    async def require_role(self, user_id: str, role_id: str) -> AuthorizationResult:
        result = await self._auth_provider.has_role(user_id, role_id)
        if not result.allowed:
            raise AuthorizationError(f"Role required: {result.reason}")
        return result

    async def get_user_roles(self, user_id: str) -> Sequence[Role]:
        return await self._auth_provider.get_roles(user_id)

    async def list_all_roles(self) -> Sequence[Role]:
        return await self._role_repo.list_roles()

    async def list_all_permissions(self) -> Sequence[Permission]:
        return await self._permission_repo.list_permissions()
