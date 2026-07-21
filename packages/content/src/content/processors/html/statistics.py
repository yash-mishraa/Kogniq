from dataclasses import dataclass


@dataclass
class HTMLProcessorStatistics:
    """Tracks statistics gathered during HTML parsing."""

    headings_extracted: int = 0
    paragraphs_extracted: int = 0
    lists_extracted: int = 0
    tables_extracted: int = 0
    code_blocks_extracted: int = 0
    blockquotes_extracted: int = 0

    total_blocks: int = 0
    character_count: int = 0
    processing_duration_ms: float = 0.0

    metadata_availability: dict[str, bool] | None = None
    confidence: float = 1.0
    processor: str = "html-standard"

    def __post_init__(self) -> None:
        if self.metadata_availability is None:
            self.metadata_availability = {"title": False, "description": False, "keywords": False}

    def to_dict(self) -> dict[str, float | int | str | dict[str, bool] | None]:
        return {
            "headings_extracted": self.headings_extracted,
            "paragraphs_extracted": self.paragraphs_extracted,
            "lists_extracted": self.lists_extracted,
            "tables_extracted": self.tables_extracted,
            "code_blocks_extracted": self.code_blocks_extracted,
            "blockquotes_extracted": self.blockquotes_extracted,
            "total_blocks": self.total_blocks,
            "character_count": self.character_count,
            "processing_duration_ms": self.processing_duration_ms,
            "metadata_availability": self.metadata_availability,
            "confidence": self.confidence,
            "processor": self.processor,
        }
