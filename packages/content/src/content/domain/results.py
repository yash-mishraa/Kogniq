from dataclasses import dataclass
from datetime import timedelta

from .entities import LearningResource, ResourceChunk, ResourceSection
from .events import DomainEvent
from .value_objects import ContentStatistics, ResourceMetadata


@dataclass(frozen=True)
class ProcessingResult:
    resource: LearningResource
    metadata: ResourceMetadata
    statistics: ContentStatistics
    sections: list[ResourceSection]
    chunks: list[ResourceChunk]
    events: list[DomainEvent]
    processing_time: timedelta
