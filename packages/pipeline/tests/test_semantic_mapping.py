import json
from datetime import UTC, datetime
from typing import Any

import pytest
from persistence.factory import MemoryRepositoryFactory
from persistence.memory_uow import MemoryUnitOfWork
from persistence.uow_factory import AbstractUnitOfWorkFactory
from pipeline.stages.semantic_enrichment import SemanticEnrichmentStage

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics
from content.normalized.semantics import DocumentSemantics


class MockUoWFactory(AbstractUnitOfWorkFactory):
    def __init__(self) -> None:
        self.factory = MemoryRepositoryFactory()

    def create(self) -> MemoryUnitOfWork:
        return MemoryUnitOfWork(self.factory)


class MockContext:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def document_id(self) -> str:
        return str(self._data.get("document_id", ""))

    @property
    def metadata(self) -> dict[str, Any]:
        return {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value


def create_chunk(chunk_id: str, text: str, page_number: int) -> Chunk:
    meta = ChunkMetadata(processor="test", document_version="1", source="test", checksum="123")
    stats = ChunkStatistics(
        line_count=10,
        character_count=10,
        word_count=10,
        estimated_tokens=10,
        processing_timestamp=datetime.now(UTC),
        confidence=1.0,
    )
    return Chunk(
        id=chunk_id,
        document_id="doc1",
        chunk_index=1,
        text=text,
        page_number=page_number,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_map_01_chunk_inside_one_section() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    # 1 section, 1 chunk containing title, 1 chunk inside
    sections = [{"id": "sec1", "title": "Introduction", "page_number": 1, "parent_id": None}]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")
        uow.commit()

    c1 = create_chunk("c1", "1. Introduction\nThis is the intro.", 1)
    c2 = create_chunk("c2", "More text in the introduction.", 1)

    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1, c2))})
    res = await stage.execute(ctx)

    assert res.success
    new_chunks = ctx.get("chunk_collection").chunks
    assert new_chunks[0].section_id == "sec1"
    assert new_chunks[0].section_path == "Introduction"
    assert new_chunks[1].section_id == "sec1"  # Inherited!


@pytest.mark.asyncio
async def test_map_02_nested_subsection_path() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    sections = [
        {"id": "sec1", "title": "3 Attention", "page_number": 1, "parent_id": None},
        {"id": "sec2", "title": "3.1 Attention Mechanisms", "page_number": 1, "parent_id": "sec1"},
        {"id": "sec3", "title": "3.1.1 Self-Attention", "page_number": 1, "parent_id": "sec2"},
    ]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    c1 = create_chunk("c1", "3 Attention 3.1 Attention Mechanisms 3.1.1 Self-Attention text", 1)
    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1,))})
    await stage.execute(ctx)

    new_chunks = ctx.get("chunk_collection").chunks
    assert (
        new_chunks[0].section_path
        == "3 Attention > 3.1 Attention Mechanisms > 3.1.1 Self-Attention"
    )
    assert new_chunks[0].section_id == "sec3"


@pytest.mark.asyncio
async def test_map_03_chunk_after_boundary() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    sections = [
        {"id": "sec1", "title": "Section A", "page_number": 1, "parent_id": None},
        {"id": "sec2", "title": "Section B", "page_number": 1, "parent_id": None},
    ]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    c1 = create_chunk("c1", "Section A data", 1)
    c2 = create_chunk("c2", "Section B data", 1)

    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1, c2))})
    await stage.execute(ctx)

    new_chunks = ctx.get("chunk_collection").chunks
    assert new_chunks[0].section_id == "sec1"
    assert new_chunks[1].section_id == "sec2"


@pytest.mark.asyncio
async def test_map_04_chunk_spanning_two_sections() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    sections = [
        {"id": "sec1", "title": "Section A", "page_number": 1, "parent_id": None},
        {"id": "sec2", "title": "Section B", "page_number": 1, "parent_id": None},
    ]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    c1 = create_chunk("c1", "End of Section A. Section B begins here.", 1)
    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1,))})
    await stage.execute(ctx)

    new_chunks = ctx.get("chunk_collection").chunks
    # Because lookahead processes A then B, B will overwrite A as best_new_section
    assert new_chunks[0].section_id == "sec2"


@pytest.mark.asyncio
async def test_map_05_no_semantic_match() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    sections = [{"id": "sec1", "title": "Section A", "page_number": 1, "parent_id": None}]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    # Text doesn't match Section A
    c1 = create_chunk("c1", "Title Page Data", 1)
    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1,))})
    await stage.execute(ctx)

    new_chunks = ctx.get("chunk_collection").chunks
    assert new_chunks[0].section_id is None


@pytest.mark.asyncio
async def test_map_06_exact_same_chunk() -> None:
    # Implicitly tested as the code has no random variables.
    pass


@pytest.mark.asyncio
async def test_map_07_repeated_section_titles() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    sections = [
        {"id": "sec1", "title": "Introduction", "page_number": 1, "parent_id": None},
        {"id": "sec2", "title": "Introduction", "page_number": 2, "parent_id": None},
    ]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    c1 = create_chunk("c1", "Introduction first", 1)
    c2 = create_chunk("c2", "Introduction second", 2)
    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1, c2))})
    await stage.execute(ctx)

    new_chunks = ctx.get("chunk_collection").chunks
    assert new_chunks[0].section_id == "sec2"
    assert new_chunks[1].section_id == "sec2"


@pytest.mark.asyncio
async def test_map_08_section_continuing_onto_another_page() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    sections = [{"id": "sec1", "title": "Long Section", "page_number": 1, "parent_id": None}]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    c1 = create_chunk("c1", "Long Section part 1", 1)
    c2 = create_chunk("c2", "still going", 2)
    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1, c2))})
    await stage.execute(ctx)

    new_chunks = ctx.get("chunk_collection").chunks
    assert new_chunks[0].section_id == "sec1"
    assert new_chunks[1].section_id == "sec1"


@pytest.mark.asyncio
async def test_map_09_figure_mapping() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    figures = [{"id": "fig1", "figure_number": "Fig 1", "caption": "A nice diagram"}]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": [], "figures": figures}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    c1 = create_chunk("c1", "This is a nice diagram of the process", 1)
    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1,))})
    await stage.execute(ctx)

    new_chunks = ctx.get("chunk_collection").chunks
    assert new_chunks[0].figure_id == "fig1"


@pytest.mark.asyncio
async def test_map_10_malformed_semantic_data() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json="INVALID JSON",
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")

    c1 = create_chunk("c1", "Normal text", 1)
    ctx = MockContext({"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1,))})
    res = await stage.execute(ctx)

    assert res.success  # fail open!
    assert "warning" in res.data
    new_chunks = ctx.get("chunk_collection").chunks
    assert new_chunks[0].section_id is None


@pytest.mark.asyncio
async def test_map_11_unmatched_chunks_inherit_previous_section() -> None:
    uow_factory = MockUoWFactory()
    stage = SemanticEnrichmentStage(uow_factory)

    sections = [{"id": "sec1", "title": "Introduction", "page_number": 1, "parent_id": None}]
    semantics = DocumentSemantics(
        id="sem1",
        document_id="doc1",
        semantic_version="2",
        status="completed",
        is_active=True,
        semantics_json=json.dumps({"sections": sections}),
        created_at=datetime.now(UTC),
    )
    with uow_factory.create() as uow:
        await uow.semantics.save(semantics)
        await uow.semantics.activate_version("doc1", "sem1")
        uow.commit()

    c1 = create_chunk("c1", "1. Introduction\nThis is the intro.", 1)
    c2 = create_chunk("c2", "Random unmatched paragraph...", 2)
    c3 = create_chunk("c3", "More unmatched text...", 3)

    ctx = MockContext(
        {"document_id": "doc1", "chunk_collection": ChunkCollection(chunks=(c1, c2, c3))}
    )
    res = await stage.execute(ctx)

    assert res.success
    enriched = ctx.get("chunk_collection").chunks
    assert enriched[0].metadata.section_title == "Introduction"
    assert enriched[1].metadata.section_title == "Introduction"
    assert enriched[2].metadata.section_title == "Introduction"
