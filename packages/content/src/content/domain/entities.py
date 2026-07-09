import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .domain_errors import InvalidChunkError, InvalidResourceError, InvalidSectionError
from .enums import ProcessingStatus, ResourceType


def generate_id() -> str:
    return str(uuid.uuid4())


@dataclass
class LearningResource:
    title: str
    resource_type: ResourceType
    source: str
    checksum: str
    language: str = "en"
    status: ProcessingStatus = ProcessingStatus.UPLOADED
    id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidResourceError("Resource title cannot be empty.")
        if not self.source or not self.source.strip():
            raise InvalidResourceError("Resource source cannot be empty.")
        if not self.checksum or not self.checksum.strip():
            raise InvalidResourceError("Resource checksum cannot be empty.")


@dataclass
class ResourceSection:
    resource_id: str
    title: str
    order: int
    page_start: int | None = None
    page_end: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    id: str = field(default_factory=generate_id)

    def __post_init__(self) -> None:
        if self.order < 0:
            raise InvalidSectionError("Section order cannot be negative.")
        if not self.title or not self.title.strip():
            raise InvalidSectionError("Section title cannot be empty.")


@dataclass
class ResourceChunk:
    resource_id: str
    section_id: str
    text: str
    order: int
    checksum: str
    token_estimate: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=generate_id)

    def __post_init__(self) -> None:
        if self.order < 0:
            raise InvalidChunkError("Chunk order cannot be negative.")
        if not self.text or not self.text.strip():
            raise InvalidChunkError("Chunk text cannot be empty.")
        if not self.checksum or not self.checksum.strip():
            raise InvalidChunkError("Chunk checksum cannot be empty.")
