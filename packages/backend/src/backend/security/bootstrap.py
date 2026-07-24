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
    ]

    existing_perms = {p.permission_id for p in await permission_repo.list_permissions()}
    for p in canonical_permissions:
        if p.permission_id not in existing_perms:
            await permission_repo.create_permission(p)
            logger.debug(f"Created permission: {p.permission_id}")

    # 2. Seed Default User Role
    user_role = await role_repo.get_role(ROLE_USER_ID)
    if not user_role:
        user_role = Role(
            role_id=ROLE_USER_ID,
            name="Standard User",
            description="Default role for authenticated users",
            permissions=(
                DOCUMENTS_READ.permission_id,
                DOCUMENTS_WRITE.permission_id,
                DOCUMENTS_DELETE.permission_id,
                LEARNING_GENERATE.permission_id,
                RETRIEVAL_SEARCH.permission_id,
                JOBS_VIEW.permission_id,
            ),
        )
        await role_repo.create_role(user_role)
        logger.info(f"Created canonical role: {ROLE_USER_ID}")

    # Optional: Seed Admin Role if needed
    admin_role = await role_repo.get_role(ROLE_ADMIN_ID)
    if not admin_role:
        admin_role = Role(
            role_id=ROLE_ADMIN_ID,
            name="Administrator",
            description="Full access",
            permissions=tuple(p.permission_id for p in canonical_permissions),
        )
        await role_repo.create_role(admin_role)
        logger.info(f"Created canonical role: {ROLE_ADMIN_ID}")


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
