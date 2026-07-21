import pytest

from auth.authorization import Permission, Role
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


@pytest.mark.asyncio
async def test_permission_and_role_creation(
    permission_repo: MemoryPermissionRepository,
    role_repo: MemoryRoleRepository,
) -> None:
    p = Permission(permission_id="docs:read", name="Read Docs", description="Read access")
    await permission_repo.create_permission(p)
    fetched_p = await permission_repo.get_permission("docs:read")
    assert fetched_p == p

    r = Role(role_id="USER", name="User", description="Standard User", permissions=("docs:read",))
    await role_repo.create_role(r)
    fetched_r = await role_repo.get_role("USER")
    assert fetched_r == r

    # Update role
    r_updated = Role(
        role_id="USER", name="User", description="Updated", 
        permissions=("docs:read", "docs:write")
    )
    await role_repo.update_role(r_updated)
    fetched_updated = await role_repo.get_role("USER")
    assert fetched_updated and "docs:write" in fetched_updated.permissions


@pytest.mark.asyncio
async def test_authorization_checks(
    role_repo: MemoryRoleRepository,
    auth_provider: MemoryAuthorizationProvider,
) -> None:
    user_id = "user-123"
    r = Role(role_id="USER", name="User", description="", permissions=("docs:read",))
    await role_repo.create_role(r)

    # Initially denies
    res_no_role = await auth_provider.has_role(user_id, "USER")
    assert not res_no_role.allowed
    assert res_no_role.evaluated_role == "USER"

    res_no_perm = await auth_provider.has_permission(user_id, "docs:read")
    assert not res_no_perm.allowed

    # Assign role
    await auth_provider.assign_role(user_id, "USER")
    
    # Duplicate assignment should not throw, just overwrite
    await auth_provider.assign_role(user_id, "USER")

    # Now has role
    res_has_role = await auth_provider.has_role(user_id, "USER")
    assert res_has_role.allowed
    assert res_has_role.reason == "Role granted"

    # Now has permission
    res_has_perm = await auth_provider.has_permission(user_id, "docs:read")
    assert res_has_perm.allowed
    assert res_has_perm.evaluated_permission == "docs:read"
    assert res_has_perm.evaluated_role == "USER"
    assert res_has_perm.reason == "Permission granted via role"

    # Remove role
    await auth_provider.remove_role(user_id, "USER")
    res_removed = await auth_provider.has_role(user_id, "USER")
    assert not res_removed.allowed


@pytest.mark.asyncio
async def test_multiple_roles_and_overlapping_permissions(
    role_repo: MemoryRoleRepository,
    auth_provider: MemoryAuthorizationProvider,
) -> None:
    user_id = "user-456"
    r1 = Role(role_id="READER", name="Reader", description="", permissions=("docs:read",))
    r2 = Role(
        role_id="WRITER", name="Writer", description="", 
        permissions=("docs:write", "docs:read")
    )
    await role_repo.create_role(r1)
    await role_repo.create_role(r2)

    await auth_provider.assign_role(user_id, "READER")
    await auth_provider.assign_role(user_id, "WRITER")

    roles = await auth_provider.get_roles(user_id)
    assert len(roles) == 2

    # Overlapping permission check
    res_read = await auth_provider.has_permission(user_id, "docs:read")
    assert res_read.allowed  # Should pass since both have it
    
    res_write = await auth_provider.has_permission(user_id, "docs:write")
    assert res_write.allowed # Passes because of WRITER

    res_delete = await auth_provider.has_permission(user_id, "docs:delete")
    assert not res_delete.allowed
