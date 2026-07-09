from dataclasses import dataclass
from datetime import datetime

from .checksum import Checksum
from .exceptions import validate_non_negative, validate_not_empty
from .lifecycle import LifecycleState
from .metadata import ResourceMetadata
from .source import ContentSource
from .stream import AbstractStreamReference


@dataclass(frozen=True, kw_only=True)
class ResourceHandle:
    """
    Immutable representation of a learning resource across all storage origins.
    Passed to content parsers in place of raw filenames or paths.
    """

    id: str
    filename: str
    extension: str
    mime_type: str
    source: ContentSource
    checksum: Checksum
    size_bytes: int
    created_at: datetime
    metadata: ResourceMetadata
    stream_reference: AbstractStreamReference
    lifecycle_state: LifecycleState

    def __post_init__(self) -> None:
        validate_not_empty(self.filename, "filename")
        validate_non_negative(self.size_bytes, "size_bytes")
