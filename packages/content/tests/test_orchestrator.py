from datetime import UTC, datetime
from typing import Any

import pytest

from content.domain import (
    ContentStatistics,
    LearningResource,
    ProcessingStatus,
    ResourceChunk,
    ResourceMetadata,
    ResourceProcessingCompleted,
    ResourceProcessingFailed,
    ResourceProcessingStarted,
    ResourceSection,
    ResourceType,
    ResourceValidated,
)
from content.normalized import (
    BlockType,
    DocumentMetadata,
    NormalizedBlock,
    NormalizedDocument,
    NormalizedPage,
)
from content.pipeline import (
    ChunkGenerator,
    ContentProcessingPipeline,
    ContentValidator,
    MetadataExtractor,
    SectionExtractor,
    StatisticsExtractor,
)
from content.plugins.interfaces import AbstractContentProcessor
from content.resource import (
    AbstractStreamReference,
    Checksum,
    ChecksumAlgorithm,
    ContentSource,
    LifecycleState,
    ResourceHandle,
    ResourceMetadata as HandleMetadata,
)


class MockStreamReference(AbstractStreamReference):
    def open_stream(self) -> Any:
        return "mock"


class MockValidator(ContentValidator):
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def validate(self, resource: LearningResource) -> tuple[bool, str]:
        if self.should_fail:
            return False, "Validation failed mock"
        return True, ""


class MockParser(AbstractContentProcessor):
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    @property
    def processor_info(self) -> Any:
        return None

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        if self.should_fail:
            raise RuntimeError("Parser failed mock")
        return NormalizedDocument(
            id="doc1",
            title="t",
            pages=(
                NormalizedPage(
                    page_number=1,
                    blocks=(
                        NormalizedBlock(
                            block_id="b1", block_type=BlockType.PARAGRAPH, text="t", order=1
                        ),
                    ),
                ),
            ),
            source="s",
            checksum="c",
            version="1.0",
            created_at=datetime.now(UTC),
            metadata=DocumentMetadata(),
        )


class MockMetadataExtractor(MetadataExtractor):
    def extract_metadata(
        self, resource: LearningResource, parsed_content: NormalizedDocument
    ) -> ResourceMetadata:
        return ResourceMetadata(language="en")


class MockSectionExtractor(SectionExtractor):
    def extract_sections(
        self, resource: LearningResource, parsed_content: NormalizedDocument
    ) -> list[ResourceSection]:
        return [ResourceSection(resource_id=resource.id, title="S1", order=1)]


class MockChunkGenerator(ChunkGenerator):
    def generate_chunks(
        self,
        resource: LearningResource,
        sections: list[ResourceSection],
        parsed_content: NormalizedDocument,
    ) -> list[ResourceChunk]:
        return [
            ResourceChunk(
                resource_id=resource.id,
                section_id=sections[0].id,
                text="t1",
                order=1,
                checksum="c1",
            )
        ]


class MockStatisticsExtractor(StatisticsExtractor):
    def extract_statistics(
        self,
        resource: LearningResource,
        sections: list[ResourceSection],
        chunks: list[ResourceChunk],
    ) -> ContentStatistics:
        return ContentStatistics(page_count=1)


@pytest.fixture
def resource() -> LearningResource:
    return LearningResource(
        title="Test",
        resource_type=ResourceType.PDF,
        source="http",
        checksum="chk",
    )


@pytest.fixture
def handle() -> ResourceHandle:
    return ResourceHandle(
        id="res_1",
        filename="test.pdf",
        extension=".pdf",
        mime_type="application/pdf",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="hash"),
        size_bytes=100,
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=MockStreamReference(),
        lifecycle_state=LifecycleState.CREATED,
    )


def test_pipeline_success(resource: LearningResource, handle: ResourceHandle) -> None:
    pipeline = ContentProcessingPipeline(
        MockValidator(),
        MockParser(),
        MockMetadataExtractor(),
        MockSectionExtractor(),
        MockChunkGenerator(),
        MockStatisticsExtractor(),
    )
    result = pipeline.process(resource, handle)

    assert result.resource.status == ProcessingStatus.PROCESSED
    assert len(result.sections) == 1
    assert len(result.chunks) == 1
    assert len(result.events) == 3
    assert isinstance(result.events[0], ResourceValidated)
    assert isinstance(result.events[1], ResourceProcessingStarted)
    assert isinstance(result.events[2], ResourceProcessingCompleted)


def test_pipeline_validator_failure(resource: LearningResource, handle: ResourceHandle) -> None:
    pipeline = ContentProcessingPipeline(
        MockValidator(should_fail=True),
        MockParser(),
        MockMetadataExtractor(),
        MockSectionExtractor(),
        MockChunkGenerator(),
        MockStatisticsExtractor(),
    )
    result = pipeline.process(resource, handle)

    assert result.resource.status == ProcessingStatus.FAILED
    assert len(result.sections) == 0
    assert len(result.events) == 2
    assert isinstance(result.events[0], ResourceValidated)
    assert isinstance(result.events[1], ResourceProcessingFailed)
    assert result.events[1].error_message == "Validation failed mock"


def test_pipeline_parser_failure(resource: LearningResource, handle: ResourceHandle) -> None:
    pipeline = ContentProcessingPipeline(
        MockValidator(),
        MockParser(should_fail=True),
        MockMetadataExtractor(),
        MockSectionExtractor(),
        MockChunkGenerator(),
        MockStatisticsExtractor(),
    )
    result = pipeline.process(resource, handle)

    assert result.resource.status == ProcessingStatus.FAILED
    assert len(result.events) == 3
    assert isinstance(result.events[2], ResourceProcessingFailed)
    assert "Parser failed mock" in result.events[2].error_message
