from dataclasses import dataclass

from .domain_errors import InvalidMetadataError, InvalidStatisticsError


@dataclass(frozen=True)
class ResourceMetadata:
    language: str
    estimated_pages: int | None = None
    estimated_tokens: int | None = None
    author: str | None = None
    publisher: str | None = None
    edition: str | None = None
    year: int | None = None
    source_url: str | None = None
    license: str | None = None

    def __post_init__(self) -> None:
        if self.estimated_pages is not None and self.estimated_pages < 0:
            raise InvalidMetadataError("estimated_pages cannot be negative.")
        if self.estimated_tokens is not None and self.estimated_tokens < 0:
            raise InvalidMetadataError("estimated_tokens cannot be negative.")


@dataclass(frozen=True)
class ContentStatistics:
    page_count: int = 0
    section_count: int = 0
    chunk_count: int = 0
    image_count: int = 0
    table_count: int = 0
    formula_count: int = 0

    def __post_init__(self) -> None:
        if self.page_count < 0:
            raise InvalidStatisticsError("page_count cannot be negative.")
        if self.section_count < 0:
            raise InvalidStatisticsError("section_count cannot be negative.")
        if self.chunk_count < 0:
            raise InvalidStatisticsError("chunk_count cannot be negative.")
        if self.image_count < 0:
            raise InvalidStatisticsError("image_count cannot be negative.")
        if self.table_count < 0:
            raise InvalidStatisticsError("table_count cannot be negative.")
        if self.formula_count < 0:
            raise InvalidStatisticsError("formula_count cannot be negative.")
