from pipeline.pipeline import DocumentIngestionPipeline

from content.chunking.engine import HybridChunkEngine
from content.chunking.strategies.fixed_size import FixedSizeChunkStrategy
from content.plugins.registry import ProcessorRegistry
from content.processors.pdf.processor import PDFProcessor


class PipelineFactory:
    """
    Constructs instances of DocumentIngestionPipeline.
    Now instantiates the real PDFProcessor and HybridChunkEngine for Phase I.
    """

    @classmethod
    def create(cls) -> DocumentIngestionPipeline:
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

        chunk_engine = HybridChunkEngine(
            fixed_strategy=FixedSizeChunkStrategy(max_characters=1500)
        )

        return DocumentIngestionPipeline(
            processor_registry=registry,
            chunk_engine=chunk_engine,
        )
