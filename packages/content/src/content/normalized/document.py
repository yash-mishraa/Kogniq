from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .metadata import DocumentMetadata
from .page import NormalizedPage
from .validation import InvalidDocumentError, validate_not_empty


@dataclass(frozen=True, kw_only=True)
class NormalizedDocument:
    """Canonical internal document format for Kogniq."""

    id: str
    title: str
    pages: tuple[NormalizedPage, ...]
    source: str
    checksum: str
    version: str
    created_at: datetime
    metadata: DocumentMetadata | None = None
    statistics: dict[str, Any] | None = None
    language: str | None = None

    def __post_init__(self) -> None:
        validate_not_empty(self.title, "title", InvalidDocumentError)
        if not self.pages:
            raise InvalidDocumentError("Document must contain at least one page.")
