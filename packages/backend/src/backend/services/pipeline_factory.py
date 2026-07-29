from typing import Any

from persistence.uow_factory import AbstractUnitOfWorkFactory
from pipeline.interfaces import PipelineStage
from pipeline.pipeline import DocumentIntelligencePipeline
from pipeline.stages.ingestion import IngestionStage

from content.chunking.engine import HybridChunkEngine
from content.chunking.strategies.fixed_size import FixedSizeChunkStrategy
from content.plugins.registry import ProcessorRegistry
from content.processors.pdf.processor import PDFProcessor
from jobs.interfaces import AbstractJobManager


class PipelineFactory:
    """
    Constructs instances of DocumentIntelligencePipeline.
    Now instantiates the real PDFProcessor and HybridChunkEngine for Phase II.
    """

    @classmethod
    def create(
        cls,
        job_manager: AbstractJobManager | None = None,
        uow_factory: AbstractUnitOfWorkFactory | None = None,
        embedding_provider: "Any | None" = None,
        vector_store: "Any | None" = None,
        knowledge_extractor: "Any | None" = None,
        generator_factory: "Any | None" = None,
    ) -> DocumentIntelligencePipeline:
        registry = ProcessorRegistry()
        registry.register(PDFProcessor())

        try:
            from content.processors.txt.processor import TXTProcessor

            registry.register(TXTProcessor())
        except ImportError:
            pass

        try:
            from content.processors.markdown.processor import MarkdownProcessor

            registry.register(MarkdownProcessor())
        except ImportError:
            pass

        chunk_engine = HybridChunkEngine(fixed_strategy=FixedSizeChunkStrategy(max_characters=1500))

        stages: list[PipelineStage] = []

        if uow_factory:
            stages.append(
                IngestionStage(
                    processor_registry=registry, chunk_engine=chunk_engine, uow_factory=uow_factory
                )
            )

        if embedding_provider and vector_store:
            from pipeline.stages.embedding import EmbeddingStage

            stages.append(EmbeddingStage(provider=embedding_provider, vector_store=vector_store))

        if knowledge_extractor and uow_factory:
            from pipeline.stages.extraction import KnowledgeExtractionStage

            stages.append(
                KnowledgeExtractionStage(extractor=knowledge_extractor, uow_factory=uow_factory)
            )

        if generator_factory and uow_factory:
            from pipeline.stages.learning import LearningGenerationStage

            generators = [
                generator_factory.get_generator(name)
                for name in ["notes", "summary", "explanation", "flashcards", "quiz", "study_guide"]
            ]
            stages.append(LearningGenerationStage(generators=generators, uow_factory=uow_factory))

        return DocumentIntelligencePipeline(
            stages=stages,
            job_manager=job_manager,
        )
