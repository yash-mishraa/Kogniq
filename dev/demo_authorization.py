import asyncio
import sys
from pathlib import Path

# Add workspace packages to path
if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    for pkg_dir in (root / "packages").iterdir():
        if pkg_dir.is_dir() and (pkg_dir / "src").exists():
            sys.path.insert(0, str(pkg_dir / "src"))

from backend.dependencies import (
    get_authentication_service,
    get_authorization_service,
    get_permission_repository,
    get_role_repository,
)
from backend.security.policies import (
    ADMIN_USERS,
    DOCUMENTS_READ,
    DOCUMENTS_WRITE,
    ROLE_ADMIN_ID,
    ROLE_USER_ID,
)

from auth.authorization import Role
from auth.models import AuthenticationRequest, AuthProvider, User


async def main() -> None:
    print("=== Kogniq Authorization Domain Demo ===")

    # 1. Get services
    auth_service = await get_authentication_service()
    authorization_service = await get_authorization_service()

    # 2. Setup standard permissions and roles in repositories
    perm_repo = get_permission_repository()
    role_repo = get_role_repository()

    await perm_repo.create_permission(DOCUMENTS_READ)
    await perm_repo.create_permission(DOCUMENTS_WRITE)
    await perm_repo.create_permission(ADMIN_USERS)

    user_role = Role(
        role_id=ROLE_USER_ID,
        name="User",
        description="Standard User",
        permissions=(DOCUMENTS_READ.permission_id,),
    )
    admin_role = Role(
        role_id=ROLE_ADMIN_ID,
        name="Admin",
        description="Administrator",
        permissions=(
            DOCUMENTS_READ.permission_id,
            DOCUMENTS_WRITE.permission_id,
            ADMIN_USERS.permission_id,
        ),
    )

    await role_repo.create_role(user_role)
    await role_repo.create_role(admin_role)
    print("\n[+] Initialized Roles: USER (read-only), ADMIN (read/write/admin)")

    # 3. Create a User
    user = User(user_id="demo-user-1", email="user@kogniq.ai", display_name="Demo User")
    await auth_service._user_repo.create_user(user)

    request = AuthenticationRequest(
        provider=AuthProvider.LOCAL, payload={"email": "user@kogniq.ai"}
    )
    result = await auth_service.authenticate(request)
    provider = result.identity.provider
    provider_uid = result.identity.provider_user_id
    print(f"\n[+] Authenticated Identity: {provider} / {provider_uid}")

    user_id = user.user_id

    # 4. Assign USER role
    print(f"\n[+] Assigning {ROLE_USER_ID} role to user...")
    await authorization_service.assign_role(user_id, ROLE_USER_ID)

    # 5. Permission Checks (USER)
    print("\n=== Permission Checks (As USER) ===")
    read_check = await authorization_service.require_permission(
        user_id, DOCUMENTS_READ.permission_id
    )
    print(f"Check {DOCUMENTS_READ.permission_id}: ALLOWED ({read_check.reason})")

    print(f"Check {DOCUMENTS_WRITE.permission_id}: ", end="")
    try:
        await authorization_service.require_permission(user_id, DOCUMENTS_WRITE.permission_id)
        print("ALLOWED")
    except Exception as e:
        print(f"DENIED ({e})")

    # 6. Promote to ADMIN
    print(f"\n[+] Promoting user to {ROLE_ADMIN_ID}...")
    await authorization_service.assign_role(user_id, ROLE_ADMIN_ID)

    # 7. Permission Checks (ADMIN)
    print("\n=== Permission Checks (As ADMIN) ===")
    write_check = await authorization_service.require_permission(
        user_id, DOCUMENTS_WRITE.permission_id
    )
    print(f"Check {DOCUMENTS_WRITE.permission_id}: ALLOWED ({write_check.reason})")

    admin_check = await authorization_service.require_permission(user_id, ADMIN_USERS.permission_id)
    print(f"Check {ADMIN_USERS.permission_id}: ALLOWED ({admin_check.reason})")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
