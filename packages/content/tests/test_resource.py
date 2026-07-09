from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from typing import Any

import pytest

from content.resource import (
    AbstractStreamReference,
    Checksum,
    ChecksumAlgorithm,
    ContentSource,
    InvalidChecksumError,
    InvalidResourceHandleError,
    LifecycleState,
    ResourceHandle,
    ResourceMetadata,
)


class MockStreamReference(AbstractStreamReference):
    """Mock stream reference for testing."""

    def open_stream(self) -> Any:
        return "mock_stream"


def test_checksum_validation() -> None:
    checksum = Checksum(algorithm=ChecksumAlgorithm.SHA256, value="abcdef123456")
    assert checksum.algorithm == ChecksumAlgorithm.SHA256
    assert checksum.value == "abcdef123456"


def test_checksum_invalid_empty() -> None:
    with pytest.raises(InvalidChecksumError, match="checksum value cannot be empty"):
        Checksum(algorithm=ChecksumAlgorithm.MD5, value="   ")


def test_resource_handle_creation() -> None:
    handle = ResourceHandle(
        id="res_1",
        filename="notes.pdf",
        extension=".pdf",
        mime_type="application/pdf",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="valid_hash"),
        size_bytes=1024,
        created_at=datetime.now(UTC),
        metadata=ResourceMetadata(attributes={"author": "Student"}),
        stream_reference=MockStreamReference(),
        lifecycle_state=LifecycleState.CREATED,
    )
    assert handle.id == "res_1"
    assert handle.filename == "notes.pdf"
    assert handle.size_bytes == 1024
    assert handle.metadata.attributes["author"] == "Student"


def test_resource_handle_invalid_filename() -> None:
    with pytest.raises(InvalidResourceHandleError, match="filename cannot be empty"):
        ResourceHandle(
            id="res_2",
            filename="",
            extension=".pdf",
            mime_type="application/pdf",
            source=ContentSource.LOCAL,
            checksum=Checksum(algorithm=ChecksumAlgorithm.MD5, value="hash"),
            size_bytes=100,
            created_at=datetime.now(UTC),
            metadata=ResourceMetadata(),
            stream_reference=MockStreamReference(),
            lifecycle_state=LifecycleState.REGISTERED,
        )


def test_resource_handle_invalid_size() -> None:
    with pytest.raises(InvalidResourceHandleError, match="size_bytes cannot be negative"):
        ResourceHandle(
            id="res_3",
            filename="invalid.txt",
            extension=".txt",
            mime_type="text/plain",
            source=ContentSource.REMOTE_URL,
            checksum=Checksum(algorithm=ChecksumAlgorithm.SHA1, value="hash"),
            size_bytes=-5,
            created_at=datetime.now(UTC),
            metadata=ResourceMetadata(),
            stream_reference=MockStreamReference(),
            lifecycle_state=LifecycleState.CREATED,
        )


def test_immutability() -> None:
    handle = ResourceHandle(
        id="res_1",
        filename="notes.pdf",
        extension=".pdf",
        mime_type="application/pdf",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="valid_hash"),
        size_bytes=1024,
        created_at=datetime.now(UTC),
        metadata=ResourceMetadata(),
        stream_reference=MockStreamReference(),
        lifecycle_state=LifecycleState.CREATED,
    )
    with pytest.raises(FrozenInstanceError):
        handle.filename = "new.pdf"  # type: ignore


def test_checksum_immutability() -> None:
    checksum = Checksum(algorithm=ChecksumAlgorithm.MD5, value="hash")
    with pytest.raises(FrozenInstanceError):
        checksum.value = "new_hash"  # type: ignore
