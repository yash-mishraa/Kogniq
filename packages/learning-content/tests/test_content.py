from datetime import UTC, datetime

import pytest

from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.exceptions import InvalidLearningContentError
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


def create_valid_metadata() -> LearningContentMetadata:
    return LearningContentMetadata(
        provider="test_provider",
        model="test_model",
        model_version="1.0",
        generation_version="1.0",
        language="en",
        educational_level="beginner",
        subject="computer_science",
        syllabus="standard",
        prompt_version="1.0",
        tags=("test",),
    )


def create_valid_statistics() -> LearningContentStatistics:
    return LearningContentStatistics(
        character_count=100,
        word_count=20,
        estimated_tokens=30,
        processing_time_ms=10.0,
        confidence=0.9,
    )


def test_learning_content_valid() -> None:
    content = LearningContent(
        id="content-1",
        source_document_id="doc-1",
        source_chunk_ids=("chunk-1",),
        content_type=ContentType.SUMMARY,
        title="Valid Title",
        body="Valid body content.",
        metadata=create_valid_metadata(),
        statistics=create_valid_statistics(),
        created_at=datetime.now(UTC),
    )
    assert content.title == "Valid Title"


def test_learning_content_empty_body() -> None:
    with pytest.raises(InvalidLearningContentError, match="Content body cannot be empty"):
        LearningContent(
            id="content-1",
            source_document_id="doc-1",
            source_chunk_ids=("chunk-1",),
            content_type=ContentType.SUMMARY,
            title="Valid Title",
            body="   ",
            metadata=create_valid_metadata(),
            statistics=create_valid_statistics(),
            created_at=datetime.now(UTC),
        )


def test_learning_content_empty_title() -> None:
    with pytest.raises(InvalidLearningContentError, match="Content title cannot be empty"):
        LearningContent(
            id="content-1",
            source_document_id="doc-1",
            source_chunk_ids=("chunk-1",),
            content_type=ContentType.SUMMARY,
            title="",
            body="Valid body",
            metadata=create_valid_metadata(),
            statistics=create_valid_statistics(),
            created_at=datetime.now(UTC),
        )


def test_learning_content_empty_chunks() -> None:
    with pytest.raises(InvalidLearningContentError, match="Source chunk IDs must not be empty"):
        LearningContent(
            id="content-1",
            source_document_id="doc-1",
            source_chunk_ids=(),
            content_type=ContentType.SUMMARY,
            title="Valid Title",
            body="Valid body",
            metadata=create_valid_metadata(),
            statistics=create_valid_statistics(),
            created_at=datetime.now(UTC),
        )
