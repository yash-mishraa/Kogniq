from abc import ABC, abstractmethod

from ..domain.entities import LearningResource, ResourceChunk, ResourceSection
from ..domain.value_objects import ContentStatistics, ResourceMetadata
from ..normalized.document import NormalizedDocument


class ContentValidator(ABC):
    """Validates the raw resource before processing begins."""

    @abstractmethod
    def validate(self, resource: LearningResource) -> tuple[bool, str]:
        pass


class MetadataExtractor(ABC):
    """Extracts semantic metadata from the resource."""

    @abstractmethod
    def extract_metadata(
        self, resource: LearningResource, parsed_content: NormalizedDocument
    ) -> ResourceMetadata:
        pass


class SectionExtractor(ABC):
    """Divides parsed content into logical sections (chapters, headers)."""

    @abstractmethod
    def extract_sections(
        self, resource: LearningResource, parsed_content: NormalizedDocument
    ) -> list[ResourceSection]:
        pass


class ChunkGenerator(ABC):
    """Generates semantic chunks from logical sections for processing and embedding."""

    @abstractmethod
    def generate_chunks(
        self,
        resource: LearningResource,
        sections: list[ResourceSection],
        parsed_content: NormalizedDocument,
    ) -> list[ResourceChunk]:
        pass


class StatisticsExtractor(ABC):
    """Computes basic statistics (page count, token count, etc.)."""

    @abstractmethod
    def extract_statistics(
        self,
        resource: LearningResource,
        sections: list[ResourceSection],
        chunks: list[ResourceChunk],
    ) -> ContentStatistics:
        pass
