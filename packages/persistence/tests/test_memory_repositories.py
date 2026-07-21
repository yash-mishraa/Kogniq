from datetime import UTC, datetime

import pytest
from knowledge.graph import KnowledgeGraph
from persistence.memory.chunk_repo import MemoryChunkRepository
from persistence.memory.document_repo import MemoryDocumentRepository
from persistence.memory.knowledge_repo import MemoryKnowledgeRepository
from persistence.memory.learning_repo import MemoryLearningRepository

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


@pytest.fixture
def doc_repo() -> MemoryDocumentRepository:
    return MemoryDocumentRepository()


@pytest.fixture
def chunk_repo() -> MemoryChunkRepository:
    return MemoryChunkRepository()


@pytest.fixture
def know_repo() -> MemoryKnowledgeRepository:
    return MemoryKnowledgeRepository()


@pytest.fixture
def learn_repo() -> MemoryLearningRepository:
    return MemoryLearningRepository()


# --- Test Document Repository ---
@pytest.mark.asyncio
async def test_document_repository_save_and_get(doc_repo: MemoryDocumentRepository) -> None:
    doc = NormalizedDocument(
        id="doc-1",
        title="Test Document",
        pages=(NormalizedPage(page_number=1, blocks=()),),
        source="test",
        checksum="123",
        version="v1",
        created_at=datetime.now(UTC),
        metadata=DocumentMetadata(author="test"),
    )

    # Save
    res = await doc_repo.save(doc)
    assert res.id == "doc-1"
    assert res.is_new is True

    # Get
    retrieved = await doc_repo.get("doc-1")
    assert retrieved is not None
    assert retrieved.id == "doc-1"
    assert retrieved.title == "Test Document"

    # Exists
    assert await doc_repo.exists("doc-1") is True
    assert await doc_repo.exists("doc-unknown") is False

    # Statistics
    stats = await doc_repo.statistics()
    assert stats.total_items == 1

    # Overwrite
    doc2 = NormalizedDocument(
        id="doc-1",
        title="Updated Document",
        pages=(NormalizedPage(page_number=1, blocks=()),),
        source="test",
        checksum="123",
        version="v2",
        created_at=datetime.now(UTC),
        metadata=doc.metadata,
    )
    res2 = await doc_repo.save(doc2)
    assert res2.is_new is False
    updated_doc = await doc_repo.get("doc-1")
    assert updated_doc is not None
    assert updated_doc.title == "Updated Document"

    # Delete
    del_res = await doc_repo.delete("doc-1")
    assert del_res.was_deleted is True
    assert await doc_repo.exists("doc-1") is False
    assert await doc_repo.get("doc-1") is None

    # Delete non-existent
    del_res2 = await doc_repo.delete("doc-1")
    assert del_res2.was_deleted is False


# --- Test Chunk Repository ---
@pytest.mark.asyncio
async def test_chunk_repository_operations(chunk_repo: MemoryChunkRepository) -> None:
    chunk = Chunk(
        id="chunk-1",
        document_id="doc-2",
        chunk_index=0,
        text="text",
        metadata=ChunkMetadata(
            processor="test", document_version="v1", source="test", checksum="1"
        ),
        statistics=ChunkStatistics(
            character_count=4,
            line_count=1,
            word_count=1,
            estimated_tokens=1,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    collection = ChunkCollection(chunks=(chunk,))

    res = await chunk_repo.save(collection)
    assert res.id == "doc-2"
    assert res.is_new is True

    retrieved = await chunk_repo.get_by_document("doc-2")
    assert retrieved is not None
    assert retrieved.chunks[0].id == "chunk-1"

    stats = await chunk_repo.statistics()
    assert stats.total_items == 1

    del_res = await chunk_repo.delete("doc-2")
    assert del_res.was_deleted is True

    # Save empty should raise ValueError
    with pytest.raises(ValueError):
        await chunk_repo.save(ChunkCollection(chunks=()))


# --- Test Knowledge Repository ---
@pytest.mark.asyncio
async def test_knowledge_repository_operations(know_repo: MemoryKnowledgeRepository) -> None:
    graph = KnowledgeGraph(concepts=(), relationships=())

    res = await know_repo.save("doc-3", graph)
    assert res.id == "doc-3"
    assert res.is_new is True

    retrieved = await know_repo.get("doc-3")
    assert retrieved is not None

    stats = await know_repo.statistics()
    assert stats.total_items == 1

    del_res = await know_repo.delete("doc-3")
    assert del_res.was_deleted is True

    # Save without document id
    bad_graph = KnowledgeGraph(concepts=(), relationships=())
    with pytest.raises(ValueError):
        await know_repo.save("", bad_graph)


# --- Test Learning Repository ---
@pytest.mark.asyncio
async def test_learning_repository_operations(learn_repo: MemoryLearningRepository) -> None:
    content = LearningContent(
        id="learn-1",
        source_document_id="doc-4",
        source_chunk_ids=("chunk-1",),
        content_type=ContentType.SUMMARY,
        title="Title",
        body="Body",
        metadata=LearningContentMetadata(
            provider="test",
            model="test-model",
            model_version="1",
            generation_version="1",
            language="en",
            educational_level="beginner",
            subject="test",
            syllabus="test",
            prompt_version="1",
            tags=("test",),
        ),
        statistics=LearningContentStatistics(
            word_count=1,
            character_count=4,
            estimated_tokens=1,
            processing_time_ms=10.0,
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )

    res = await learn_repo.save(content)
    assert res.id == "learn-1"
    assert res.is_new is True

    retrieved = await learn_repo.get("learn-1")
    assert retrieved is not None
    assert retrieved.id == "learn-1"

    listed = await learn_repo.list_by_document("doc-4")
    assert len(listed) == 1
    assert listed[0].id == "learn-1"

    stats = await learn_repo.statistics()
    assert stats.total_items == 1

    del_res = await learn_repo.delete("learn-1")
    assert del_res.was_deleted is True
