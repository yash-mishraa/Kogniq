from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LearningGenerationResult:
    status: str
    document_id: str
    generator: str
    title: str
    content_type: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)
