import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
for pkg_dir in (root / "packages").iterdir():
    if pkg_dir.is_dir() and (pkg_dir / "src").exists():
        sys.path.insert(0, str(pkg_dir / "src"))

import time  # noqa: E402
from datetime import UTC  # noqa: E402
from threading import Thread  # noqa: E402

import httpx  # noqa: E402
import uvicorn  # noqa: E402
from backend.app import create_app  # noqa: E402


def start_server() -> None:
    app = create_app()
    
    from backend.dependencies import get_authorization_service
    from backend.services.authorization_service import AuthorizationService
    from auth.authorization import AuthorizationResult

    class MockAuthorizationService(AuthorizationService):
        def __init__(self) -> None:
            pass

        async def require_permission(self, user_id: str, permission_id: str) -> AuthorizationResult:
            return AuthorizationResult(allowed=True, reason="Demo")

    app.dependency_overrides[get_authorization_service] = MockAuthorizationService

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")


def main() -> None:
    print("Starting backend server...")
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to boot
    time.sleep(3)

    # 1. Create a dummy Markdown document
    test_file_path = root / "demo_doc.md"
    content = """# Machine Learning Basics
    
Gradient descent is an optimization algorithm commonly used to train machine learning models and
neural networks. Training data helps these models learn over time.

Overfitting occurs when a model learns the training data too well, capturing noise instead of the
underlying pattern, leading to poor generalization.

Photosynthesis is a process used by plants and other organisms to convert light energy into
chemical energy.
"""
    test_file_path.write_text(content, encoding="utf-8")

    try:
        print("\n--- 1. Processing Document ---")
        with test_file_path.open("rb") as f:
            files = {"file": ("demo_doc.md", f, "text/markdown")}
            response = httpx.post(
                "http://127.0.0.1:8001/api/v1/documents/process", files=files, timeout=30.0
            )

        if response.status_code != 200:
            print(f"Failed to process document: {response.text}")
            return

        doc_id = response.json()["document_id"]
        print(f"Document processed successfully. ID: {doc_id}")

        # Populate repositories manually since pipeline is stubbed
        import asyncio
        from datetime import datetime
        from typing import cast

        from backend.dependencies import get_retrieval_factory, get_uow_factory
        from retrieval.semantic_retriever import SemanticRetriever

        from content.chunking.chunk import Chunk
        from content.chunking.collection import ChunkCollection
        from content.chunking.metadata import ChunkMetadata
        from content.chunking.statistics import ChunkStatistics

        async def populate() -> None:

            chunks = []
            paragraphs = [
                p.strip() for p in content.split("\n\n") if p.strip() and not p.startswith("#")
            ]
            for i, p in enumerate(paragraphs):
                chunk = Chunk(
                    id=f"{doc_id}-chunk-{i}",
                    document_id=doc_id,
                    chunk_index=i,
                    text=p,
                    metadata=ChunkMetadata(
                        processor="demo", source="demo_doc.md", document_version="1", checksum="abc"
                    ),
                    statistics=ChunkStatistics(
                        character_count=len(p),
                        line_count=1,
                        word_count=len(p.split()),
                        estimated_tokens=len(p.split()),
                        processing_timestamp=datetime.now(UTC),
                        confidence=1.0,
                    ),
                    created_at=datetime.now(UTC),
                )
                chunks.append(chunk)

            collection = ChunkCollection(chunks=tuple(chunks))
            with get_uow_factory().create() as uow:
                await uow.chunks.save(collection)

            # Populate vector store
            retriever = get_retrieval_factory().get_retriever()
            semantic_retriever = cast(SemanticRetriever, retriever)
            embeddings = semantic_retriever._provider.generate_batch(collection)
            semantic_retriever._store.store_batch(embeddings)

        asyncio.run(populate())

        print("\n--- 2. Executing Semantic Searches ---")
        queries = [
            "What is gradient descent?",
            "Explain overfitting.",
            "Photosynthesis",
            "Random unrelated query about spaceships",
        ]

        for q in queries:
            print(f"\nQuery: '{q}'")
            payload = {"document_id": doc_id, "query": q, "top_k": 3, "minimum_similarity": 0.3}
            res = httpx.post(
                "http://127.0.0.1:8001/api/v1/retrieval/search", json=payload, timeout=10.0
            )

            if res.status_code != 200:
                print(f"Search failed: {res.text}")
                continue

            data = res.json()
            print(f"Found {data['total_results']} results in {data['processing_time_ms']:.2f}ms")
            for i, result in enumerate(data["results"]):
                short_chunk = result["chunk_text"][:60]
                print(
                    f"  [{i + 1}] Score: {result['similarity_score']:.4f} | Chunk: {short_chunk}..."
                )
            if data.get("warnings"):
                print(f"  Warnings: {data['warnings']}")

    finally:
        if test_file_path.exists():
            test_file_path.unlink()
        print("\nDemo finished.")


if __name__ == "__main__":
    main()
