from dataclasses import dataclass
from typing import Any


@dataclass
class PDFProcessorStatistics:
    pages_processed: int = 0
    blocks_extracted: int = 0
    processing_duration_ms: float = 0.0
    metadata_available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "pages_processed": self.pages_processed,
            "blocks_extracted": self.blocks_extracted,
            "processing_duration_ms": self.processing_duration_ms,
            "metadata_available": self.metadata_available,
            "processor": "fitz",
        }
