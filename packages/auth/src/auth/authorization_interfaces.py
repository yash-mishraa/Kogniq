import abc
from collections.abc import Sequence

from auth.authorization import AuthorizationResult, Permission, Role


class AbstractPermissionRepository(abc.ABC):
    @abc.abstractmethod
    async def create_permission(self, permission: Permission) -> None: ...

    @abc.abstractmethod
    async def get_permission(self, permission_id: str) -> Permission | None: ...

    @abc.abstractmethod
    async def list_permissions(self) -> Sequence[Permission]: ...

    @abc.abstractmethod
    async def update_permission(self, permission: Permission) -> None: ...

    @abc.abstractmethod
    async def delete_permission(self, permission_id: str) -> None: ...


class AbstractRoleRepository(abc.ABC):
    @abc.abstractmethod
    async def create_role(self, role: Role) -> None: ...

    @abc.abstractmethod
    async def update_role(self, role: Role) -> None: ...

    @abc.abstractmethod
    async def delete_role(self, role_id: str) -> None: ...

    @abc.abstractmethod
    async def get_role(self, role_id: str) -> Role | None: ...

    @abc.abstractmethod
    async def list_roles(self) -> Sequence[Role]: ...


class AbstractAuthorizationProvider(abc.ABC):
    @abc.abstractmethod
    async def assign_role(self, user_id: str, role_id: str) -> None: ...

    @abc.abstractmethod
    async def remove_role(self, user_id: str, role_id: str) -> None: ...

    @abc.abstractmethod
    async def get_roles(self, user_id: str) -> Sequence[Role]: ...

    @abc.abstractmethod
    async def has_permission(self, user_id: str, permission_id: str) -> AuthorizationResult: ...

    @abc.abstractmethod
    async def has_role(self, user_id: str, role_id: str) -> AuthorizationResult: ...
