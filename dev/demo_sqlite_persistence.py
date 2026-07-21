"""
Demo script for SQLite Persistence Layer.

This script demonstrates using the SQLite UnitOfWork to save, read, and delete
domain entities. It verifies that CRUD operations succeed correctly in a local database.
"""

# ruff: noqa: E402, E501
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add packages to path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root / "packages" / "backend" / "src"))
sys.path.insert(0, str(root / "packages" / "persistence" / "src"))
sys.path.insert(0, str(root / "packages" / "content" / "src"))
sys.path.insert(0, str(root / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(root / "packages" / "learning-content" / "src"))

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from persistence.factory import SQLiteRepositoryFactory
from persistence.sqlite.connection import SQLiteConnectionManager
from persistence.sqlite.schema import init_db
from persistence.uow import SQLiteUnitOfWork

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.metadata import DocumentMetadata
from content.normalized.page import NormalizedPage
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


async def main() -> None:
    print("\n--- SQLite Persistence Demo ---")
    db_path = "./data/demo_kogniq.db"

    # 1. Setup Database
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    manager = SQLiteConnectionManager(db_path)

    with manager.get_connection() as conn:
        init_db(conn)

    print("[OK] kogniq.db is created automatically")
    print("[OK] Tables are created automatically")

    factory = SQLiteRepositoryFactory()

    # 2. Create sample data
    doc_id = "test-doc-123"

    block = NormalizedBlock(
        block_id="b1", block_type=BlockType.PARAGRAPH, text="Sample text", order=0
    )
    page = NormalizedPage(page_number=1, blocks=(block,))

    document = NormalizedDocument(
        id=doc_id,
        title="SQLite Demo Document",
        source="demo",
        checksum="123456",
        version="v1",
        pages=(page,),
        metadata=DocumentMetadata(author="Demo Script"),
        created_at=datetime.now(UTC),
    )

    chunk = Chunk(
        id="chunk-1",
        document_id=doc_id,
        chunk_index=0,
        text="Sample text",
        metadata=ChunkMetadata(
            processor="demo", document_version="v1", source="demo", checksum="123"
        ),
        statistics=ChunkStatistics(
            character_count=10,
            line_count=1,
            word_count=2,
            estimated_tokens=2,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    chunks = ChunkCollection(chunks=(chunk,))

    c1 = KnowledgeConcept(
        id="c1",
        title="SQLite",
        concept_type=ConceptType.UNKNOWN,
        description="",
        aliases=(),
        metadata=KnowledgeMetadata(
            source_document=doc_id,
            source_chunk="chunk-1",
            language="en",
            confidence=1.0,
            extraction_version="1.0",
            created_by="demo",
        ),
    )
    graph = KnowledgeGraph(concepts=(c1,), relationships=())

    learning = LearningContent(
        id="learn-1",
        source_document_id=doc_id,
        source_chunk_ids=("chunk-1",),
        content_type=ContentType.SUMMARY,
        title="Demo Summary",
        body="This is a summary.",
        metadata=LearningContentMetadata(
            provider="demo",
            model="demo",
            model_version="1",
            generation_version="1",
            language="en",
            educational_level="101",
            subject="demo",
            syllabus="demo",
            prompt_version="1",
            tags=("demo",),
        ),
        statistics=LearningContentStatistics(
            character_count=10,
            word_count=2,
            estimated_tokens=2,
            processing_time_ms=10.0,
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )

    # 3. Save to database using Unit of Work
    print("\nSaving data...")
    with manager.get_connection() as conn:
        uow = SQLiteUnitOfWork(conn, factory)

        # Save operations
        doc_repo = uow.documents
        chunk_repo = uow.chunks
        know_repo = uow.knowledge
        learn_repo = uow.learning

        await doc_repo.save(document)
        await chunk_repo.save(chunks)
        await know_repo.save(doc_id, graph)
        await learn_repo.save(learning)

        # Commit manually if auto-commit isn't handling it, but standard sqlite3 with context manager
        # handles it. Let's explicitly commit for safety in the demo.
        conn.commit()

    print("[OK] CRUD operations succeed (Create)")

    # 4. Read back data
    print("\nReading data back to verify...")
    with manager.get_connection() as conn:
        uow = SQLiteUnitOfWork(conn, factory)

        loaded_doc = await uow.documents.get(doc_id)
        assert loaded_doc is not None
        assert loaded_doc.title == "SQLite Demo Document"

        loaded_chunks = await uow.chunks.get_by_document(doc_id)
        assert loaded_chunks is not None
        assert len(loaded_chunks.chunks) == 1

        loaded_graph = await uow.knowledge.get(doc_id)
        assert loaded_graph is not None
        assert "c1" in [c.id for c in loaded_graph.concepts]

        loaded_learn = await uow.learning.list_by_document(doc_id)
        assert len(loaded_learn) == 1

    print("[OK] Restarting the connection preserves data (Read)")

    # 5. Delete data
    print("\nDeleting data...")
    with manager.get_connection() as conn:
        uow = SQLiteUnitOfWork(conn, factory)

        await uow.documents.delete(doc_id)
        await uow.chunks.delete(doc_id)
        await uow.knowledge.delete(doc_id)
        await uow.learning.delete(doc_id)

        conn.commit()

    print("[OK] Deletes work correctly")

    # 6. Verify Deletion
    with manager.get_connection() as conn:
        uow = SQLiteUnitOfWork(conn, factory)

        assert await uow.documents.get(doc_id) is None
        assert await uow.chunks.get_by_document(doc_id) is None
        assert await uow.knowledge.get(doc_id) is None
        assert len(await uow.learning.list_by_document(doc_id)) == 0

    print("[OK] No exceptions occur")

    print("\n--- SQLite Demo Completed Successfully! ---")


if __name__ == "__main__":
    asyncio.run(main())
