import pytest
from backend.security.policies import DOCUMENTS_READ, OwnershipPolicy
from backend.services.authorization_service import AuthorizationError, AuthorizationService

from auth.authorization import Role
from auth.authorization_memory import (
    MemoryAuthorizationProvider,
    MemoryPermissionRepository,
    MemoryRoleRepository,
)


@pytest.fixture
def permission_repo() -> MemoryPermissionRepository:
    return MemoryPermissionRepository()


@pytest.fixture
def role_repo() -> MemoryRoleRepository:
    return MemoryRoleRepository()


@pytest.fixture
def auth_provider(
    role_repo: MemoryRoleRepository, permission_repo: MemoryPermissionRepository
) -> MemoryAuthorizationProvider:
    return MemoryAuthorizationProvider(role_repo=role_repo, permission_repo=permission_repo)


@pytest.fixture
def auth_service(
    auth_provider: MemoryAuthorizationProvider,
    role_repo: MemoryRoleRepository,
    permission_repo: MemoryPermissionRepository,
) -> AuthorizationService:
    return AuthorizationService(
        auth_provider=auth_provider,
        role_repo=role_repo,
        permission_repo=permission_repo,
    )


@pytest.mark.asyncio
async def test_require_permission(
    auth_service: AuthorizationService,
    permission_repo: MemoryPermissionRepository,
    role_repo: MemoryRoleRepository,
) -> None:
    await permission_repo.create_permission(DOCUMENTS_READ)
    
    r = Role(
        role_id="USER", name="User", description="", 
        permissions=(DOCUMENTS_READ.permission_id,)
    )
    await role_repo.create_role(r)
    
    user_id = "user-123"
    
    # Fails initially
    with pytest.raises(AuthorizationError):
        await auth_service.require_permission(user_id, DOCUMENTS_READ.permission_id)
        
    await auth_service.assign_role(user_id, "USER")
    
    # Should succeed now
    res = await auth_service.require_permission(user_id, DOCUMENTS_READ.permission_id)
    assert res.allowed
    
    await auth_service.remove_role(user_id, "USER")
    
    with pytest.raises(AuthorizationError):
        await auth_service.require_permission(user_id, DOCUMENTS_READ.permission_id)


@pytest.mark.asyncio
async def test_require_role(
    auth_service: AuthorizationService,
    role_repo: MemoryRoleRepository,
) -> None:
    r = Role(role_id="ADMIN", name="Admin", description="", permissions=())
    await role_repo.create_role(r)
    
    user_id = "admin-1"
    
    with pytest.raises(AuthorizationError):
        await auth_service.require_role(user_id, "ADMIN")
        
    await auth_service.assign_role(user_id, "ADMIN")
    
    res = await auth_service.require_role(user_id, "ADMIN")
    assert res.allowed


def test_ownership_policy() -> None:
    user_id = "user-1"
    other_user = "user-2"
    
    # Admin override
    res = OwnershipPolicy.evaluate(user_id, other_user, is_admin=True)
    assert res.allowed
    
    # Owner access
    res = OwnershipPolicy.evaluate(user_id, user_id, is_admin=False)
    assert res.allowed
    
    # Unowned resource
    res = OwnershipPolicy.evaluate(user_id, None, is_admin=False)
    assert res.allowed
    
    # Denied access
    res = OwnershipPolicy.evaluate(user_id, other_user, is_admin=False)
    assert not res.allowed
