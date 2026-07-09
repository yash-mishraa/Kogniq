import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


def generate_event_id() -> str:
    return str(uuid.uuid4())


def current_time() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events."""

    resource_id: str
    event_id: str = field(default_factory=generate_event_id)
    occurred_at: datetime = field(default_factory=current_time)


@dataclass(frozen=True, kw_only=True)
class ResourceUploaded(DomainEvent):
    source: str
    resource_type: str


@dataclass(frozen=True, kw_only=True)
class ResourceValidated(DomainEvent):
    is_valid: bool
    validation_message: str | None = None


@dataclass(frozen=True, kw_only=True)
class ResourceProcessingStarted(DomainEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class ResourceProcessingCompleted(DomainEvent):
    sections_extracted: int
    chunks_generated: int


@dataclass(frozen=True, kw_only=True)
class ResourceProcessingFailed(DomainEvent):
    error_message: str
