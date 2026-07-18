from abc import ABC, abstractmethod

from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.providers.provider_info import GeneratorInfo


class AbstractLearningGenerator(ABC):
    """Base interface for all educational content generators."""

    @abstractmethod
    def info(self) -> GeneratorInfo:
        """Get metadata about this generator."""
        ...

    @abstractmethod
    def generate(self, chunks: ChunkCollection, graph: KnowledgeGraph) -> LearningContent:
        """Generate learning content from a chunk collection and knowledge graph."""
        ...

    @abstractmethod
    def generate_batch(
        self, collections: tuple[ChunkCollection, ...], graphs: tuple[KnowledgeGraph, ...]
    ) -> LearningContentCollection:
        """Generate multiple learning contents from batches of chunks and graphs."""
        ...
