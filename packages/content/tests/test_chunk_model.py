from datetime import UTC, datetime

import pytest

from content.chunking import (
    Chunk,
    ChunkCollection,
    ChunkMetadata,
    ChunkStatistics,
    InvalidChunkError,
)


def create_valid_metadata() -> ChunkMetadata:
    return ChunkMetadata(
        processor="markdown", document_version="1.0", source="test.md", checksum="abcd123"
    )


def create_valid_statistics() -> ChunkStatistics:
    return ChunkStatistics(
        character_count=100,
        line_count=5,
        word_count=20,
        estimated_tokens=25,
        processing_timestamp=datetime.now(UTC),
        confidence=0.95,
    )


def test_chunk_valid_instantiation() -> None:
    chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        text="This is a valid chunk.",
        metadata=create_valid_metadata(),
        statistics=create_valid_statistics(),
        created_at=datetime.now(UTC),
    )
    assert chunk.id == "chunk-1"
    assert chunk.text == "This is a valid chunk."


def test_chunk_immutability() -> None:
    chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        text="This is a valid chunk.",
        metadata=create_valid_metadata(),
        statistics=create_valid_statistics(),
        created_at=datetime.now(UTC),
    )
    from dataclasses import FrozenInstanceError

    with pytest.raises(FrozenInstanceError):
        chunk.text = "Attempted mutation"  # type: ignore


def test_invalid_metadata_does_not_exist() -> None:
    # We rely on standard Python type checks and frozen dataclasses for ChunkMetadata
    # But let's check a missing mandatory field
    with pytest.raises(TypeError):
        ChunkMetadata(processor="test")  # type: ignore


def test_invalid_statistics() -> None:
    # Negative character count
    with pytest.raises(InvalidChunkError):
        ChunkStatistics(
            character_count=-1,
            line_count=5,
            word_count=20,
            estimated_tokens=25,
            processing_timestamp=datetime.now(UTC),
            confidence=0.9,
        )

    # Confidence out of bounds
    with pytest.raises(InvalidChunkError):
        ChunkStatistics(
            character_count=100,
            line_count=5,
            word_count=20,
            estimated_tokens=25,
            processing_timestamp=datetime.now(UTC),
            confidence=1.5,
        )


def test_invalid_chunk_validation() -> None:
    # Empty ID
    with pytest.raises(InvalidChunkError):
        Chunk(
            id="",
            document_id="doc-1",
            chunk_index=0,
            text="Valid text",
            metadata=create_valid_metadata(),
            statistics=create_valid_statistics(),
            created_at=datetime.now(UTC),
        )

    # Empty Text
    with pytest.raises(InvalidChunkError):
        Chunk(
            id="chunk-1",
            document_id="doc-1",
            chunk_index=0,
            text="   ",
            metadata=create_valid_metadata(),
            statistics=create_valid_statistics(),
            created_at=datetime.now(UTC),
        )

    # Negative chunk index
    with pytest.raises(InvalidChunkError):
        Chunk(
            id="chunk-1",
            document_id="doc-1",
            chunk_index=-1,
            text="Valid text",
            metadata=create_valid_metadata(),
            statistics=create_valid_statistics(),
            created_at=datetime.now(UTC),
        )


def test_chunk_collection_aggregates() -> None:
    chunk1 = Chunk(
        id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        text="First chunk",
        metadata=create_valid_metadata(),
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
    chunk2 = Chunk(
        id="chunk-2",
        document_id="doc-1",
        chunk_index=1,
        text="Second chunk is longer",
        metadata=create_valid_metadata(),
        statistics=ChunkStatistics(
            character_count=20,
            line_count=2,
            word_count=4,
            estimated_tokens=5,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )

    collection = ChunkCollection(chunks=(chunk1, chunk2))

    assert collection.total_chunks == 2
    assert collection.total_characters == 30
    assert collection.total_words == 6
    assert collection.total_estimated_tokens == 8


def test_duplicate_chunk_indexes_different_documents() -> None:
    # This is allowed business logic
    chunk1 = Chunk(
        id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        text="First chunk of doc 1",
        metadata=create_valid_metadata(),
        statistics=create_valid_statistics(),
        created_at=datetime.now(UTC),
    )
    chunk2 = Chunk(
        id="chunk-2",
        document_id="doc-2",
        chunk_index=0,
        text="First chunk of doc 2",
        metadata=create_valid_metadata(),
        statistics=create_valid_statistics(),
        created_at=datetime.now(UTC),
    )

    collection = ChunkCollection(chunks=(chunk1, chunk2))
    assert collection.total_chunks == 2


def test_empty_collection() -> None:
    collection = ChunkCollection(chunks=())
    assert collection.total_chunks == 0
    assert collection.total_characters == 0
    assert collection.total_words == 0
    assert collection.total_estimated_tokens == 0
