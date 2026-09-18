from datetime import UTC, datetime

import pytest

from content.domain.entities import LearningResource
from content.domain.enums import ResourceType
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.metadata import DocumentMetadata
from content.normalized.page import NormalizedPage
from content.pipeline.components.chunk import DefaultChunkGenerator
from content.pipeline.components.metadata import DefaultMetadataExtractor
from content.pipeline.components.section import DefaultSectionExtractor
from content.pipeline.components.statistics import DefaultStatisticsExtractor
from content.pipeline.components.validator import DefaultContentValidator


@pytest.fixture
def sample_resource() -> LearningResource:
    return LearningResource(
        title="Sample",
        resource_type=ResourceType.TEXT,
        source="http://example.com/sample.txt",
        checksum="hash",
    )


@pytest.fixture
def sample_normalized_document() -> NormalizedDocument:
    return NormalizedDocument(
        id="doc-1",
        title="Sample",
        pages=(
            NormalizedPage(
                page_number=1,
                blocks=(
                    NormalizedBlock(
                        block_id="b1", block_type=BlockType.HEADING, text="Heading 1", order=1
                    ),
                    NormalizedBlock(
                        block_id="b2", block_type=BlockType.PARAGRAPH, text="Para 1", order=2
                    ),
                ),
            ),
            NormalizedPage(
                page_number=2,
                blocks=(
                    NormalizedBlock(
                        block_id="b3", block_type=BlockType.HEADING, text="Heading 2", order=3
                    ),
                    NormalizedBlock(
                        block_id="b4", block_type=BlockType.PARAGRAPH, text="Para 2", order=4
                    ),
                ),
            ),
        ),
        source="upload",
        checksum="hash",
        version="1.0",
        created_at=datetime.now(UTC),
        metadata=DocumentMetadata(author="Test Author"),
    )


def test_validator(sample_resource: LearningResource) -> None:
    validator = DefaultContentValidator()
    is_valid, _msg = validator.validate(sample_resource)
    assert is_valid is True

    # LearningResource __post_init__ handles basic empty checks, but
    # the validator can perform deeper checks if needed.


def test_metadata_extractor(
    sample_resource: LearningResource, sample_normalized_document: NormalizedDocument
) -> None:
    extractor = DefaultMetadataExtractor()
    meta = extractor.extract_metadata(sample_resource, sample_normalized_document)
    assert meta.language == "en"  # from resource defaults
    assert meta.author == "Test Author"
    assert meta.source_url == "http://example.com/sample.txt"


def test_section_extractor(
    sample_resource: LearningResource, sample_normalized_document: NormalizedDocument
) -> None:
    extractor = DefaultSectionExtractor()
    sections = extractor.extract_sections(sample_resource, sample_normalized_document)
    # Start section + 2 headings = 3 sections
    assert len(sections) == 3
    assert sections[1].title == "Heading 1"
    assert sections[2].title == "Heading 2"
    assert sections[2].page_start == 2
    assert sections[2].page_end == 2


def test_chunk_generator(
    sample_resource: LearningResource, sample_normalized_document: NormalizedDocument
) -> None:
    section_extractor = DefaultSectionExtractor()
    sections = section_extractor.extract_sections(sample_resource, sample_normalized_document)

    chunk_generator = DefaultChunkGenerator()
    chunks = chunk_generator.generate_chunks(sample_resource, sections, sample_normalized_document)

    assert len(chunks) > 0
    assert chunks[0].section_id is not None
    assert chunks[0].resource_id == sample_resource.id


def test_statistics_extractor(
    sample_resource: LearningResource, sample_normalized_document: NormalizedDocument
) -> None:
    section_extractor = DefaultSectionExtractor()
    sections = section_extractor.extract_sections(sample_resource, sample_normalized_document)

    chunk_generator = DefaultChunkGenerator()
    chunks = chunk_generator.generate_chunks(sample_resource, sections, sample_normalized_document)

    stats_extractor = DefaultStatisticsExtractor()
    stats = stats_extractor.extract_statistics(sample_resource, sections, chunks)

    assert stats.section_count == 3
    assert stats.chunk_count == len(chunks)
    assert stats.page_count >= 1
