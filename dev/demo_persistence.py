import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

from knowledge.graph import KnowledgeGraph

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics
from content.normalized.document import NormalizedDocument
from content.normalized.metadata import DocumentMetadata
from content.normalized.page import NormalizedPage
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "packages" / "persistence" / "src"))
sys.path.insert(0, str(root / "packages" / "content" / "src"))
sys.path.insert(0, str(root / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(root / "packages" / "learning-content" / "src"))

from persistence.factory import RepositoryFactory  # noqa: E402


async def main() -> None:
    print("--- Kogniq Persistence Demo ---")

    factory = RepositoryFactory()
    doc_repo = factory.get_document_repository()
    chunk_repo = factory.get_chunk_repository()
    know_repo = factory.get_knowledge_repository()
    learn_repo = factory.get_learning_repository()

    # 1. Document Repository
    print("\n[Document Repository]")
    doc = NormalizedDocument(
        id="doc-demo-1",
        title="Test Document",
        pages=(NormalizedPage(page_number=1, blocks=()),),
        source="demo",
        checksum="123",
        version="v1",
        created_at=datetime.now(UTC),
        metadata=DocumentMetadata(author="demo"),
    )
    print("Saving document...")
    res = await doc_repo.save(doc)
    print(f"Saved: {res}")

    print("Retrieving document...")
    retrieved_doc = await doc_repo.get("doc-demo-1")
    print(f"Retrieved: {retrieved_doc.title if retrieved_doc else 'None'}")

    print("Updating document...")
    doc_updated = NormalizedDocument(
        id="doc-demo-1",
        title="Updated test document.",
        pages=(NormalizedPage(page_number=1, blocks=()),),
        source="demo",
        checksum="123",
        version="v1",
        created_at=datetime.now(UTC),
        metadata=doc.metadata,
    )
    res_update = await doc_repo.save(doc_updated)
    print(f"Updated (is_new={res_update.is_new})")

    print("Deleting document...")
    del_res = await doc_repo.delete("doc-demo-1")
    print(f"Deleted: {del_res}")

    # 2. Chunk Repository
    print("\n[Chunk Repository]")
    chunk = Chunk(
        id="chunk-demo-1",
        document_id="doc-demo-2",
        chunk_index=0,
        text="Chunk text",
        metadata=ChunkMetadata(
            processor="demo", document_version="v1", source="demo", checksum="1"
        ),
        statistics=ChunkStatistics(
            character_count=10,
            line_count=1,
            word_count=2,
            estimated_tokens=3,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    collection = ChunkCollection(chunks=(chunk,))
    print("Saving chunk collection...")
    res2 = await chunk_repo.save(collection)
    print(f"Saved: {res2}")

    print("Retrieving chunk collection...")
    retrieved_chunks = await chunk_repo.get_by_document("doc-demo-2")
    print(f"Retrieved {len(retrieved_chunks.chunks) if retrieved_chunks else 0} chunks.")

    print("Deleting chunk collection...")
    del_res2 = await chunk_repo.delete("doc-demo-2")
    print(f"Deleted: {del_res2}")

    # 3. Knowledge Repository
    print("\n[Knowledge Repository]")
    graph = KnowledgeGraph(concepts=(), relationships=())
    print("Saving knowledge graph...")
    res3 = await know_repo.save("doc-demo-3", graph)
    print(f"Saved: {res3}")

    print("Retrieving knowledge graph...")
    retrieved_graph = await know_repo.get("doc-demo-3")
    print(
        f"Retrieved graph with {len(retrieved_graph.concepts) if retrieved_graph else 0} concepts."
    )

    print("Deleting knowledge graph...")
    del_res3 = await know_repo.delete("doc-demo-3")
    print(f"Deleted: {del_res3}")

    # 4. Learning Repository
    print("\n[Learning Repository]")
    content = LearningContent(
        id="learn-demo-1",
        source_document_id="doc-demo-4",
        source_chunk_ids=("chunk-1",),
        content_type=ContentType.SUMMARY,
        title="Demo Summary",
        body="This is a demo summary.",
        metadata=LearningContentMetadata(
            provider="demo",
            model="demo-model",
            model_version="1",
            generation_version="1",
            language="en",
            educational_level="beginner",
            subject="demo",
            syllabus="demo",
            prompt_version="1",
            tags=("demo",),
        ),
        statistics=LearningContentStatistics(
            word_count=5,
            character_count=23,
            estimated_tokens=6,
            processing_time_ms=5.0,
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    print("Saving learning artifact...")
    res4 = await learn_repo.save(content)
    print(f"Saved: {res4}")

    print("Retrieving learning artifact...")
    retrieved_learn = await learn_repo.get("learn-demo-1")
    print(f"Retrieved: {retrieved_learn.title if retrieved_learn else 'None'}")

    print("Retrieving artifacts by document...")
    listed = await learn_repo.list_by_document("doc-demo-4")
    print(f"Listed {len(listed)} artifacts for document.")

    print("Deleting learning artifact...")
    del_res4 = await learn_repo.delete("learn-demo-1")
    print(f"Deleted: {del_res4}")

    print("\n--- Demo Complete ---")


if __name__ == "__main__":
    asyncio.run(main())
