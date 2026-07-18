import time
from abc import ABC, abstractmethod

from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.generators.base.exceptions import LearningGenerationError
from learning_content.generators.base.interfaces import AbstractContentParser, AbstractPromptBuilder
from learning_content.generators.base.models import GenerationContext, GenerationMetadata
from learning_content.providers.base import AbstractTextGenerationProvider
from learning_content.providers.interfaces import AbstractLearningGenerator


class BaseLearningGenerator(AbstractLearningGenerator, ABC):
    """
    Reusable orchestration framework for learning content generators.
    Decouples prompt building, text generation, and response parsing.
    """

    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        """
        Initialize the base generator with a provider.

        Args:
            provider: The injected text generation provider.
        """
        self._provider = provider

    @property
    @abstractmethod
    def prompt_builder(self) -> AbstractPromptBuilder:
        """Concrete generators must supply their prompt builder."""
        ...

    @property
    @abstractmethod
    def parser(self) -> AbstractContentParser:
        """Concrete generators must supply their parser."""
        ...

    @property
    @abstractmethod
    def prompt_version(self) -> str:
        """Concrete generators must supply their prompt version."""
        ...

    def before_generate(self, context: GenerationContext) -> None:
        """Lifecycle hook before generation begins."""

    def after_generate(self, content: LearningContent) -> None:
        """Lifecycle hook after content is generated and parsed."""

    def generate(self, chunks: ChunkCollection, graph: KnowledgeGraph) -> LearningContent:
        """
        Orchestrates the complete generation workflow.
        """
        context = GenerationContext(chunks=chunks, graph=graph)

        self.before_generate(context)

        try:
            # 1. Build prompt
            prompt = self.prompt_builder.build(context)

            # 2. Invoke provider and time it
            start_time = time.perf_counter()
            raw_response = self._provider.generate(prompt)
            end_time = time.perf_counter()
            generation_time_ms = (end_time - start_time) * 1000.0

            # 3. Construct Metadata
            metadata = GenerationMetadata(
                provider_name=self._provider.info.provider_id,
                model_name=self._provider.info.default_model,
                model_version=self._provider.info.model_version,
                generation_version="1.0",
                prompt_version=self.prompt_version,
                generation_time_ms=generation_time_ms,
            )

            # 4. Parse
            content = self.parser.parse(raw_response, context, metadata)

            self.after_generate(content)

            return content

        except Exception as e:
            if isinstance(e, LearningGenerationError):
                raise
            raise LearningGenerationError(f"Failed to generate learning content: {e}") from e

    def generate_batch(
        self, collections: tuple[ChunkCollection, ...], graphs: tuple[KnowledgeGraph, ...]
    ) -> LearningContentCollection:
        """
        Default sequential implementation for batch generation.
        Concrete generators can override this if optimized batching is available.
        """
        if len(collections) != len(graphs):
            raise LearningGenerationError("Mismatched collections and graphs lengths.")

        contents = []
        for chunks, graph in zip(collections, graphs, strict=True):
            contents.append(self.generate(chunks, graph))

        return LearningContentCollection(contents=tuple(contents))
