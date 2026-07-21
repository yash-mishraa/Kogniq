import asyncio
import sys
from pathlib import Path

# Setup paths dynamically for the demo
root = Path(__file__).resolve().parent.parent
for pkg_dir in (root / "packages").iterdir():
    if pkg_dir.is_dir() and (pkg_dir / "src").exists():
        sys.path.insert(0, str(pkg_dir / "src"))

from backend.dependencies import get_authentication_service  # noqa: E402

from auth.models import AuthenticationRequest, AuthProvider, User  # noqa: E402


async def main() -> None:
    print("--- Kogniq Auth Domain Demo ---")
    
    # Obtain service through standard Dependency Injection entrypoint
    service = await get_authentication_service()
    
    print("\n1. Creating User")
    user = User(
        user_id="usr_abc123",
        email="developer@kogniq.ai",
        display_name="Kogniq Dev"
    )
    created = await service.create_user(user)
    print(f"Created: {created}")
    
    print("\n2. Authenticating via LOCAL provider")
    request = AuthenticationRequest(
        provider=AuthProvider.LOCAL,
        payload={"email": "developer@kogniq.ai"}
    )
    result = await service.authenticate(request)
    provider_str = result.identity.provider
    user_id_str = result.identity.provider_user_id
    print(f"Authenticated Identity: {provider_str} / {user_id_str}")
    if not result.session:
        print("Failed to establish session.")
        return
        
    session_id = result.session.session_id
    print(f"Session Created: {session_id} (Expires: {result.session.expires_at})")
    
    print("\n3. Resolving Current User from Session")
    current_user = await service.get_current_user(session_id)
    if current_user:
        print(f"Resolved User: {current_user.display_name} ({current_user.email})")
    else:
        print("Failed to resolve user.")
        
    print("\n4. Logging Out (Revoking Session)")
    await service.logout(session_id)
    
    print("\n5. Attempting to Resolve Current User Again")
    current_user_after = await service.get_current_user(session_id)
    if current_user_after:
        print(f"ERROR: Session still active for {current_user_after.email}")
    else:
        print("Successfully validated that the session was revoked.")
        
    print("\nDemo Completed Successfully.")


if __name__ == "__main__":
    asyncio.run(main())
