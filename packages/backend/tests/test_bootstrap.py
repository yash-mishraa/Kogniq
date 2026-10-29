"""Bootstrap reconciliation tests.

These cover the restart path that previously left durable users without any
authorization role, which surfaced as an unexpected ``403`` on document upload
even though the session cookie was valid.
"""

from datetime import UTC, datetime

import pytest
from backend.security.bootstrap import bootstrap_authorization, bootstrap_user_roles
from backend.security.policies import ROLE_ADMIN_ID, ROLE_USER_ID

from auth.authorization import Role
from auth.authorization_memory import (
    MemoryAuthorizationProvider,
    MemoryPermissionRepository,
    MemoryRoleRepository,
)
from auth.memory import MemoryUserRepository
from auth.models import User


def _provider() -> tuple[
    MemoryAuthorizationProvider,
    MemoryRoleRepository,
    MemoryPermissionRepository,
]:
    role_repo = MemoryRoleRepository()
    permission_repo = MemoryPermissionRepository()
    return (
        MemoryAuthorizationProvider(role_repo=role_repo, permission_repo=permission_repo),
        role_repo,
        permission_repo,
    )


@pytest.mark.asyncio
async def test_bootstrap_reconciles_missing_permissions_on_existing_roles() -> None:
    _, role_repo, permission_repo = _provider()
    await bootstrap_authorization(role_repo, permission_repo)
    user_role = await role_repo.get_role(ROLE_USER_ID)
    assert user_role is not None

    # Simulate a role created by an older build that predates documents:write.
    await role_repo.update_role(
        Role(
            role_id=user_role.role_id,
            name=user_role.name,
            description=user_role.description,
            permissions=("documents:read",),
        )
    )

    await bootstrap_authorization(role_repo, permission_repo)

    reconciled = await role_repo.get_role(ROLE_USER_ID)
    assert reconciled is not None
    assert "documents:write" in reconciled.permissions
    assert "documents:read" in reconciled.permissions


@pytest.mark.asyncio
async def test_bootstrap_user_roles_grants_default_role_after_restart() -> None:
    provider, role_repo, permission_repo = _provider()
    await bootstrap_authorization(role_repo, permission_repo)

    users = MemoryUserRepository()
    now = datetime.now(UTC)
    await users.create_user(
        User(
            user_id="user-1",
            email="person@example.com",
            display_name="Person",
            created_at=now,
            updated_at=now,
        )
    )
    await users.create_user(
        User(
            user_id="user-2",
            email="admin@kogniq.ai",
            display_name="Demo Admin",
            created_at=now,
            updated_at=now,
        )
    )

    granted = await bootstrap_user_roles(users, provider, admin_email="admin@kogniq.ai")

    assert granted == 2
    assert (await provider.has_role("user-1", ROLE_USER_ID)).allowed
    assert (await provider.has_role("user-2", ROLE_ADMIN_ID)).allowed
    result = await provider.has_permission("user-1", "documents:write")
    assert result.allowed

    # Idempotent: a second pass must not regrant or duplicate anything.
    assert await bootstrap_user_roles(users, provider) == 0


@pytest.mark.asyncio
async def test_bootstrap_user_roles_does_not_overwrite_existing_assignment() -> None:
    provider, role_repo, permission_repo = _provider()
    await bootstrap_authorization(role_repo, permission_repo)

    users = MemoryUserRepository()
    now = datetime.now(UTC)
    await users.create_user(
        User(
            user_id="user-1",
            email="person@example.com",
            display_name="Person",
            created_at=now,
            updated_at=now,
        )
    )
    await provider.assign_role("user-1", ROLE_ADMIN_ID)

    assert await bootstrap_user_roles(users, provider) == 0
    assert (await provider.has_role("user-1", ROLE_ADMIN_ID)).allowed
