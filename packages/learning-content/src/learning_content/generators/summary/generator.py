from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.generators.summary.exceptions import SummaryGenerationError
from learning_content.generators.summary.parser import SummaryParser
from learning_content.generators.summary.prompt_builder import SummaryPromptBuilder
from learning_content.providers.interfaces import AbstractLearningGenerator
from learning_content.providers.provider_info import GeneratorInfo
from learning_content.providers.text_generation import AbstractTextGenerationProvider


class SummaryGenerator(AbstractLearningGenerator):
    """
    Concrete implementation for generating educational summaries.
    
    This acts as an orchestrator, decoupling prompt construction and response parsing
    from the actual text generation which is handled by an injected provider.
    """

    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        """
        Initialize the generator.
        
        Args:
            provider: The text generation provider to use.
        """
        self._provider = provider
        self._prompt_builder = SummaryPromptBuilder()
        self._parser = SummaryParser()

    def info(self) -> GeneratorInfo:
        """Get metadata about this generator."""
        return GeneratorInfo(
            generator_id="summary-generator-v1",
            generator_name="Summary Generator",
            generator_version="1.0",
            provider_name=self._provider.provider_id,
            supported_content_types=(ContentType.SUMMARY,),
            maximum_chunks=100,  # Arbitrary limit, dependent on provider context window
            maximum_tokens=4000, # Arbitrary limit
            supports_batch_generation=False,
        )

    def generate(
        self, chunks: ChunkCollection, graph: KnowledgeGraph
    ) -> LearningContent:
        """
        Generate a summary from the provided chunks and graph.
        
        Orchestrates the prompt builder, provider, and parser.
        
        Args:
            chunks: The source content.
            graph: The knowledge graph for key concepts and relationships.
            
        Returns:
            The generated LearningContent.
            
        Raises:
            SummaryGenerationError: If the process fails.
        """
        try:
            prompt = self._prompt_builder.build(chunks, graph)
            raw_response = self._provider.generate(prompt)
            return self._parser.parse(raw_response, chunks, self._provider)
        except Exception as e:
            if isinstance(e, SummaryGenerationError):
                raise
            raise SummaryGenerationError(f"Failed to generate summary: {e}") from e

    def generate_batch(
        self, collections: tuple[ChunkCollection, ...], graphs: tuple[KnowledgeGraph, ...]
    ) -> LearningContentCollection:
        """
        Generate multiple summaries. Batching is not inherently optimized here.
        """
        if len(collections) != len(graphs):
            raise SummaryGenerationError("Mismatched collections and graphs lengths.")
            
        contents = []
        for chunks, graph in zip(collections, graphs, strict=True):
            contents.append(self.generate(chunks, graph))
            
        return LearningContentCollection(contents=tuple(contents))
