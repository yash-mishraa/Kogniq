import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from application.auth.register_user import RegisterUserUseCase

from backend.security.policies import (
    DOCUMENTS_DELETE,
    DOCUMENTS_READ,
    DOCUMENTS_WRITE,
    JOBS_VIEW,
    LEARNING_GENERATE,
    RETRIEVAL_SEARCH,
    ROLE_ADMIN_ID,
    ROLE_USER_ID,
)

from auth.authorization import Permission, Role
from auth.authorization_interfaces import AbstractPermissionRepository, AbstractRoleRepository

logger = logging.getLogger(__name__)


async def bootstrap_authorization(
    role_repo: AbstractRoleRepository,
    permission_repo: AbstractPermissionRepository,
) -> None:
    """Idempotently seed the authorization repositories with canonical roles and permissions."""

    # 1. Seed Permissions
    canonical_permissions: Sequence[Permission] = [
        DOCUMENTS_READ,
        DOCUMENTS_WRITE,
        DOCUMENTS_DELETE,
        LEARNING_GENERATE,
        RETRIEVAL_SEARCH,
        JOBS_VIEW,
        Permission("agent:tutor:chat", "Tutor Chat", "Can use the tutor"),
    ]

    existing_perms = {p.permission_id for p in await permission_repo.list_permissions()}
    for p in canonical_permissions:
        if p.permission_id not in existing_perms:
            await permission_repo.create_permission(p)
            logger.debug(f"Created permission: {p.permission_id}")

    # 2. Seed Default User Role
    user_permissions = (
        DOCUMENTS_READ.permission_id,
        DOCUMENTS_WRITE.permission_id,
        DOCUMENTS_DELETE.permission_id,
        LEARNING_GENERATE.permission_id,
        RETRIEVAL_SEARCH.permission_id,
        JOBS_VIEW.permission_id,
        "agent:tutor:chat",
    )
    user_role = await role_repo.get_role(ROLE_USER_ID)
    if not user_role:
        user_role = Role(
            role_id=ROLE_USER_ID,
            name="Standard User",
            description="Default role for authenticated users",
            permissions=user_permissions,
        )
        await role_repo.create_role(user_role)
        logger.info(f"Created canonical role: {ROLE_USER_ID}")
    else:
        # Roles created by older builds may predate a permission. Reconcile the
        # canonical role so upgrades do not leave users unable to upload.
        missing = tuple(p for p in user_permissions if p not in user_role.permissions)
        if missing:
            await role_repo.update_role(
                Role(
                    role_id=user_role.role_id,
                    name=user_role.name,
                    description=user_role.description,
                    permissions=user_role.permissions + missing,
                )
            )
            logger.info("Granted missing permissions to %s: %s", ROLE_USER_ID, missing)

    # Optional: Seed Admin Role if needed
    admin_permissions = tuple(p.permission_id for p in canonical_permissions)
    admin_role = await role_repo.get_role(ROLE_ADMIN_ID)
    if not admin_role:
        admin_role = Role(
            role_id=ROLE_ADMIN_ID,
            name="Administrator",
            description="Full access",
            permissions=admin_permissions,
        )
        await role_repo.create_role(admin_role)
        logger.info(f"Created canonical role: {ROLE_ADMIN_ID}")
    else:
        missing = tuple(p for p in admin_permissions if p not in admin_role.permissions)
        if missing:
            await role_repo.update_role(
                Role(
                    role_id=admin_role.role_id,
                    name=admin_role.name,
                    description=admin_role.description,
                    permissions=admin_role.permissions + missing,
                )
            )
            logger.info("Granted missing permissions to %s: %s", ROLE_ADMIN_ID, missing)


async def bootstrap_user_roles(
    user_repo: object,
    auth_provider: object,
    admin_email: str | None = None,
) -> int:
    """Ensure persisted users have a role after a restart.

    Role assignments live in the in-process authorization provider, while users
    and sessions are durable. Without this reconciliation, every restart left
    existing accounts with no roles, so uploads failed with ``403`` even though
    the session was valid. Users are granted the default role; the development
    demo account also receives the administrator role.
    """
    from auth.authorization_interfaces import AbstractAuthorizationProvider
    from auth.interfaces import AbstractUserRepository

    if not isinstance(user_repo, AbstractUserRepository):
        return 0
    if not isinstance(auth_provider, AbstractAuthorizationProvider):
        return 0

    granted = 0
    for user in await user_repo.list_users():
        if await auth_provider.get_roles(user.user_id):
            continue
        role_id = (
            ROLE_ADMIN_ID
            if admin_email and user.email.lower() == admin_email.lower()
            else ROLE_USER_ID
        )
        await auth_provider.assign_role(user.user_id, role_id)
        granted += 1
    if granted:
        logger.info("Granted default roles to %s persisted user(s)", granted)
    return granted


async def bootstrap_development_demo(use_case: "RegisterUserUseCase") -> None:
    """Idempotently seed a demo user for development and testing environments."""
    from application.auth.register_user import RegisterUserCommand
    from auth.exceptions import UserAlreadyExistsError

    try:
        await use_case.execute(
            RegisterUserCommand(
                email="admin@kogniq.ai", password="password", display_name="Demo Admin"
            )
        )
        logger.info("Seeded development demo user: admin@kogniq.ai")
    except UserAlreadyExistsError:
        logger.debug("Demo user already exists, skipping seed.")


def adopt_orphaned_documents(demo_email: str = "admin@kogniq.ai") -> int:
    """Attach legacy documents to the seeded demo user in local environments.

    Early Kogniq builds used in-memory authentication, so restarting the API
    generated a new user id and left previously uploaded documents pointing at
    an id that no longer exists. Those rows are unreachable through the API.
    This one-time, development-only repair re-homes documents whose owner is
    not present in ``users`` onto the demo account. It never runs in
    production, and it never touches documents that still have a live owner.
    """
    import sqlite3

    from backend.core.settings import settings

    if settings.persistence_provider != "sqlite":
        return 0

    connection = sqlite3.connect(settings.sqlite_database_path)
    try:
        row = connection.execute(
            "SELECT id FROM users WHERE email = ?", (demo_email,)
        ).fetchone()
        if row is None:
            return 0
        demo_user_id = row[0]
        cursor = connection.execute(
            """
            UPDATE documents
               SET user_id = ?
             WHERE user_id IS NULL
                OR user_id NOT IN (SELECT id FROM users)
            """,
            (demo_user_id,),
        )
        connection.commit()
        adopted = cursor.rowcount
    finally:
        connection.close()

    if adopted:
        logger.info("Adopted %s orphaned document(s) for %s", adopted, demo_email)
    return adopted
