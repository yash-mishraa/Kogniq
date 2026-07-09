from dataclasses import dataclass
from typing import Any


@dataclass
class MarkdownProcessorStatistics:
    headings_extracted: int = 0
    paragraphs_extracted: int = 0
    lists_extracted: int = 0
    code_blocks_extracted: int = 0
    tables_extracted: int = 0
    processing_duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "headings_extracted": self.headings_extracted,
            "paragraphs_extracted": self.paragraphs_extracted,
            "lists_extracted": self.lists_extracted,
            "code_blocks_extracted": self.code_blocks_extracted,
            "tables_extracted": self.tables_extracted,
            "processing_duration_ms": self.processing_duration_ms,
            "processor": "markdown-it-py",
        }
