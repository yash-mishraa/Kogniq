from dataclasses import dataclass
from typing import Any


@dataclass
class TXTProcessorStatistics:
    headings_extracted: int = 0
    paragraphs_extracted: int = 0
    total_blocks: int = 0
    line_count: int = 0
    character_count: int = 0
    processing_duration_ms: float = 0.0
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "headings_extracted": self.headings_extracted,
            "paragraphs_extracted": self.paragraphs_extracted,
            "total_blocks": self.total_blocks,
            "line_count": self.line_count,
            "character_count": self.character_count,
            "processing_duration_ms": self.processing_duration_ms,
            "confidence": self.confidence,
            "processor": "txt-standard",
        }
