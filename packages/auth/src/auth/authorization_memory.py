import threading
from collections.abc import Sequence

from auth.authorization import AuthorizationResult, Permission, Role, UserRole
from auth.authorization_interfaces import (
    AbstractAuthorizationProvider,
    AbstractPermissionRepository,
    AbstractRoleRepository,
)


class MemoryPermissionRepository(AbstractPermissionRepository):
    def __init__(self) -> None:
        self._permissions: dict[str, Permission] = {}
        self._lock = threading.Lock()

    async def create_permission(self, permission: Permission) -> None:
        with self._lock:
            self._permissions[permission.permission_id] = permission

    async def get_permission(self, permission_id: str) -> Permission | None:
        with self._lock:
            return self._permissions.get(permission_id)

    async def list_permissions(self) -> Sequence[Permission]:
        with self._lock:
            return list(self._permissions.values())

    async def update_permission(self, permission: Permission) -> None:
        with self._lock:
            self._permissions[permission.permission_id] = permission

    async def delete_permission(self, permission_id: str) -> None:
        with self._lock:
            self._permissions.pop(permission_id, None)


class MemoryRoleRepository(AbstractRoleRepository):
    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}
        self._lock = threading.Lock()

    async def create_role(self, role: Role) -> None:
        with self._lock:
            self._roles[role.role_id] = role

    async def update_role(self, role: Role) -> None:
        with self._lock:
            self._roles[role.role_id] = role

    async def delete_role(self, role_id: str) -> None:
        with self._lock:
            self._roles.pop(role_id, None)

    async def get_role(self, role_id: str) -> Role | None:
        with self._lock:
            return self._roles.get(role_id)

    async def list_roles(self) -> Sequence[Role]:
        with self._lock:
            return list(self._roles.values())


class MemoryAuthorizationProvider(AbstractAuthorizationProvider):
    def __init__(
        self,
        role_repo: AbstractRoleRepository,
        permission_repo: AbstractPermissionRepository,
    ) -> None:
        self._role_repo = role_repo
        self._permission_repo = permission_repo
        self._user_roles: dict[str, dict[str, UserRole]] = {}
        self._lock = threading.Lock()

    async def assign_role(self, user_id: str, role_id: str) -> None:
        with self._lock:
            if user_id not in self._user_roles:
                self._user_roles[user_id] = {}
            self._user_roles[user_id][role_id] = UserRole(user_id=user_id, role_id=role_id)

    async def remove_role(self, user_id: str, role_id: str) -> None:
        with self._lock:
            if user_id in self._user_roles:
                self._user_roles[user_id].pop(role_id, None)

    async def get_roles(self, user_id: str) -> Sequence[Role]:
        with self._lock:
            user_role_ids = list(self._user_roles.get(user_id, {}).keys())
        
        roles = []
        for role_id in user_role_ids:
            role = await self._role_repo.get_role(role_id)
            if role:
                roles.append(role)
        return roles

    async def has_permission(self, user_id: str, permission_id: str) -> AuthorizationResult:
        roles = await self.get_roles(user_id)
        for role in roles:
            if permission_id in role.permissions:
                return AuthorizationResult(
                    allowed=True,
                    reason="Permission granted via role",
                    evaluated_permission=permission_id,
                    evaluated_role=role.role_id,
                )
        return AuthorizationResult(
            allowed=False,
            reason="User does not have required permission",
            evaluated_permission=permission_id,
            evaluated_role=None,
        )

    async def has_role(self, user_id: str, role_id: str) -> AuthorizationResult:
        with self._lock:
            user_role_ids = self._user_roles.get(user_id, {})
            has_it = role_id in user_role_ids
            
        if has_it:
            return AuthorizationResult(
                allowed=True,
                reason="Role granted",
                evaluated_permission=None,
                evaluated_role=role_id,
            )
        return AuthorizationResult(
            allowed=False,
            reason="User does not have required role",
            evaluated_permission=None,
            evaluated_role=role_id,
        )
