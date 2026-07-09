import pytest

from content.domain import (
    ContentStatistics,
    InvalidChunkError,
    InvalidMetadataError,
    InvalidResourceError,
    InvalidSectionError,
    InvalidStatisticsError,
    LearningResource,
    ResourceChunk,
    ResourceMetadata,
    ResourceSection,
    ResourceType,
)


def test_learning_resource_validation() -> None:
    with pytest.raises(InvalidResourceError, match="title cannot be empty"):
        LearningResource(title="", resource_type=ResourceType.PDF, source="http", checksum="abc")
    with pytest.raises(InvalidResourceError, match="source cannot be empty"):
        LearningResource(title="A", resource_type=ResourceType.PDF, source="", checksum="abc")
    with pytest.raises(InvalidResourceError, match="checksum cannot be empty"):
        LearningResource(title="A", resource_type=ResourceType.PDF, source="http", checksum="")


def test_resource_section_validation() -> None:
    with pytest.raises(InvalidSectionError, match="order cannot be negative"):
        ResourceSection(resource_id="1", title="Title", order=-1)
    with pytest.raises(InvalidSectionError, match="title cannot be empty"):
        ResourceSection(resource_id="1", title="", order=1)


def test_resource_chunk_validation() -> None:
    with pytest.raises(InvalidChunkError, match="order cannot be negative"):
        ResourceChunk(resource_id="1", section_id="2", text="hello", order=-1, checksum="abc")
    with pytest.raises(InvalidChunkError, match="text cannot be empty"):
        ResourceChunk(resource_id="1", section_id="2", text="", order=1, checksum="abc")
    with pytest.raises(InvalidChunkError, match="checksum cannot be empty"):
        ResourceChunk(resource_id="1", section_id="2", text="hello", order=1, checksum="")


def test_metadata_validation() -> None:
    with pytest.raises(InvalidMetadataError, match="cannot be negative"):
        ResourceMetadata(language="en", estimated_pages=-1)
    with pytest.raises(InvalidMetadataError, match="cannot be negative"):
        ResourceMetadata(language="en", estimated_tokens=-1)


def test_statistics_validation() -> None:
    with pytest.raises(InvalidStatisticsError, match="cannot be negative"):
        ContentStatistics(page_count=-1)
