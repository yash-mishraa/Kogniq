from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship
from pipeline.pipeline import DefaultPipelineContext
from pipeline.stages.extraction import KnowledgeExtractionStage

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics


@pytest.fixture
def chunk_collection() -> ChunkCollection:
    chunk = Chunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        text="A transformer uses attention.",
        metadata=ChunkMetadata(
            processor="test",
            document_version="1",
            source="test",
            checksum="123",
        ),
        statistics=ChunkStatistics(
            character_count=10,
            line_count=1,
            word_count=5,
            estimated_tokens=2,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    return ChunkCollection(chunks=(chunk,))


@pytest.fixture
def mock_extractor() -> AsyncMock:
    extractor = AsyncMock()

    meta = KnowledgeMetadata(
        source_document="doc1",
        source_chunk="c1",
        language="en",
        confidence=0.99,
        extraction_version="1.0",
        created_by="mock",
    )

    concept = KnowledgeConcept(
        id="concept1",
        document_id="doc1",
        name="Transformer",
        description="A model",
        concept_type=ConceptType.THEORY,
        aliases=(),
        confidence=0.95,
        created_at=datetime.now(UTC),
        metadata=meta,
    )

    rel = KnowledgeRelationship(
        id="rel1",
        document_id="doc1",
        source_concept="concept1",
        target_concept="concept2",
        relationship_type=RelationshipType.RELATED_TO,
        confidence=0.95,
        created_at=datetime.now(UTC),
        metadata=meta,
    )

    extractor.extract.return_value = KnowledgeExtractionResult(
        graph=KnowledgeGraph(
            concepts=(concept,),
            relationships=(rel,),
        ),
        extractor_id="mock",
        extractor_name="Mock Extractor",
        version="1.0",
        processing_time_ms=10,
        processed_chunks=1,
        created_at=datetime.now(UTC),
    )
    return extractor


@pytest.fixture
def mock_uow_factory() -> MagicMock:
    factory = MagicMock()
    uow = MagicMock()

    # Setup async methods for repositories
    uow.concepts.save_all = AsyncMock()
    uow.relationships.save_all = AsyncMock()

    factory.create.return_value = uow
    uow.__enter__.return_value = uow
    return factory


@pytest.mark.asyncio
async def test_extraction_stage_success(
    chunk_collection: ChunkCollection,
    mock_extractor: AsyncMock,
    mock_uow_factory: MagicMock,
) -> None:
    stage = KnowledgeExtractionStage(
        extractor=mock_extractor,
        uow_factory=mock_uow_factory,
    )

    context = DefaultPipelineContext()
    context.set("document_id", "doc1")
    context.set("chunk_collection", chunk_collection)

    assert await stage.can_skip(context) is False

    result = await stage.execute(context)

    assert result.success is True
    assert result.data["concepts_extracted"] == 1
    assert result.data["relationships_extracted"] == 1

    # Check if uow was called
    uow = mock_uow_factory.create.return_value
    uow.concepts.save_all.assert_called_once()
    uow.relationships.save_all.assert_called_once()


@pytest.mark.asyncio
async def test_extraction_stage_skip_if_no_chunks() -> None:
    stage = KnowledgeExtractionStage(
        extractor=MagicMock(),
        uow_factory=MagicMock(),
    )
    context = DefaultPipelineContext()
    context.set("document_id", "doc1")

    # Should skip if chunk_collection is missing
    assert await stage.can_skip(context) is True

    # Should skip if chunk_collection is empty
    context.set("chunk_collection", ChunkCollection(chunks=()))
    assert await stage.can_skip(context) is True


@pytest.mark.asyncio
async def test_extraction_stage_handles_extractor_error(
    chunk_collection: ChunkCollection,
    mock_extractor: AsyncMock,
    mock_uow_factory: MagicMock,
) -> None:
    mock_extractor.extract.side_effect = Exception("API Error")

    stage = KnowledgeExtractionStage(
        extractor=mock_extractor,
        uow_factory=mock_uow_factory,
    )

    context = DefaultPipelineContext()
    context.set("document_id", "doc1")
    context.set("chunk_collection", chunk_collection)

    result = await stage.execute(context)

    # Should degrade gracefully
    assert result.success is True
    assert "warning" in result.data
    assert "Knowledge extraction failed" in result.data["warning"]
