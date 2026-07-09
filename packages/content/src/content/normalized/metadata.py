from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True)
class DocumentMetadata:
    """Metadata extracted from the original document."""

    author: str | None = None
    publisher: str | None = None
    subject: str | None = None
    keywords: tuple[str, ...] | None = None
    creation_date: datetime | None = None
    modified_date: datetime | None = None
    generator: str | None = None
    producer: str | None = None
