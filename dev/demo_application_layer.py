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
    get_document_service,
    get_learning_service,
    get_retrieval_service,
)

from application.document.commands import ProcessDocumentCommand
from application.document.process_document import ProcessDocumentUseCase
from application.learning.commands import GenerateLearningCommand
from application.learning.generate_learning import GenerateLearningUseCase
from application.retrieval.commands import RetrievalCommand
from application.retrieval.retrieve import RetrieveUseCase
from auth.models import User


async def main() -> None:
    print("=== Kogniq Application Layer Demo ===\n")

    # 1. Setup Auth
    print("[+] Initializing user and permissions...")
    await get_authentication_service()
    user = User(user_id="demo-user-1", email="dev@kogniq.ai", display_name="Developer")
    from auth.authorization import Permission, Role

    authorization_service = await get_authorization_service()
    await authorization_service._permission_repo.create_permission(
        Permission(permission_id="documents:write", name="doc write", description="")
    )
    await authorization_service._permission_repo.create_permission(
        Permission(permission_id="learning:generate", name="learn", description="")
    )
    await authorization_service._permission_repo.create_permission(
        Permission(permission_id="retrieval:search", name="retrieve", description="")
    )
    await authorization_service._role_repo.create_role(
        Role(
            role_id="ADMIN",
            name="Admin",
            description="",
            permissions=("documents:write", "learning:generate", "retrieval:search"),
        )
    )

    # 2. Get Use Cases natively (no HTTP layer needed!)
    from backend.dependencies import get_authorization_provider

    provider = get_authorization_provider()
    await provider.assign_role(user.user_id, "ADMIN")

    auth_svc = await get_authentication_service()
    doc_svc = await get_document_service()
    learn_svc = await get_learning_service()
    ret_svc = await get_retrieval_service()

    process_uc = ProcessDocumentUseCase(auth_svc, authorization_service, doc_svc)  # type: ignore
    learn_uc = GenerateLearningUseCase(auth_svc, authorization_service, learn_svc)  # type: ignore
    retrieve_uc = RetrieveUseCase(auth_svc, authorization_service, ret_svc)  # type: ignore

    # 3. Process Document
    print("\n[1] Processing Document natively via Use Case...")
    doc_cmd = ProcessDocumentCommand(
        user_id=user.user_id,
        filename="notes.md",
        content_type="text/markdown",
        size_bytes=24,
        content=b"# Architecture\nUse Cases!",
    )
    doc_result = await process_uc.execute(doc_cmd)
    print(
        f"    Success: Document {doc_result.document_id} "
        f"processed in {doc_result.processing_time_ms}ms"
    )

    # 4. Generate Learning
    print("\n[2] Generating Learning Material natively via Use Case...")
    learn_cmd = GenerateLearningCommand(
        user_id=user.user_id,
        document_id=doc_result.document_id,
        generator="summary",
    )
    try:
        learn_result = await learn_uc.execute(learn_cmd)
        print(f"    Success: {learn_result.title} generated.")
    except Exception as e:
        print(f"    (Expected) Pipeline Error: {e}")

    # 5. Retrieve Information
    print("\n[3] Semantic Search natively via Use Case...")
    search_cmd = RetrievalCommand(
        user_id=user.user_id,
        document_id=doc_result.document_id,
        query="important concepts",
        top_k=3,
    )
    try:
        search_result = await retrieve_uc.execute(search_cmd)
        print(f"    Success: Found {len(search_result.results)} chunks.")
    except Exception as e:
        print(f"    (Expected) Pipeline Error: {e}")
        search_result = None

    if search_result:
        for match in search_result.results:
            print(f"      - Score: {match.score}, Content: {match.content}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
