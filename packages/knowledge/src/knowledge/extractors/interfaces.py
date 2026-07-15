from abc import ABC, abstractmethod

from content.chunking import ChunkCollection
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.extractors.provider_info import KnowledgeExtractorInfo


class AbstractKnowledgeExtractor(ABC):
    """The canonical interface for all Knowledge Extractors."""

    @property
    @abstractmethod
    def info(self) -> KnowledgeExtractorInfo:
        """Get the extractor's capabilities and metadata."""
        ...

    @abstractmethod
    def extract(self, chunks: ChunkCollection) -> KnowledgeExtractionResult:
        """Extract a KnowledgeGraph from a collection of chunks."""
        ...

    @abstractmethod
    def extract_batch(
        self, collections: tuple[ChunkCollection, ...]
    ) -> tuple[KnowledgeExtractionResult, ...]:
        """Extract multiple KnowledgeGraphs from a batch of chunk collections."""
        ...
