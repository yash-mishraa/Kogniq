import logging
import time
from datetime import UTC, datetime

from content.chunking.engine import HybridChunkEngine
from content.plugins.registry import ProcessorRegistry
from content.resource.handle import ResourceHandle

from .exceptions import PipelineExecutionError
from .result import (
    ContentPipelineResult,
    IngestionPipelineResult,
    PipelineExecutionMetadata,
)

logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    """
    Orchestration layer that handles the first half of the document intelligence pipeline:
    Upload -> Parse -> Normalize -> Chunk -> Persist.
    Future phases will extend this to include Embed -> Index ->
    Extract Knowledge -> Generate Learning.
    """

    def __init__(
        self,
        processor_registry: ProcessorRegistry,
        chunk_engine: HybridChunkEngine,
    ) -> None:
        self.processor_registry = processor_registry
        self.chunk_engine = chunk_engine

    def run(self, handle: ResourceHandle) -> IngestionPipelineResult:
        """
        Executes the ingestion phase of the document intelligence pipeline.
        """
        start_time = time.perf_counter()
        started_at = datetime.now(UTC)

        logger.info(f"Starting ingestion pipeline for resource: {handle.id}")

        try:
            # 1. Resolve processor and normalize document
            logger.info("Resolving processor...")
            processor = self.processor_registry.processor_for_resource(handle)
            logger.info(f"Processor resolved: {processor.processor_info.name}. Processing...")
            document = processor.process(handle)

            # 2. Chunk document
            logger.info("Chunking document...")
            chunks = self.chunk_engine.chunk(document)
            logger.info(f"Generated {chunks.total_chunks} chunks.")

            content_result = ContentPipelineResult(
                document=document,
                chunks=chunks,
            )

            completed_at = datetime.now(UTC)
            end_time = time.perf_counter()

            metadata = PipelineExecutionMetadata(
                started_at=started_at,
                completed_at=completed_at,
                total_processing_time_ms=(end_time - start_time) * 1000,
                processor_name=processor.processor_info.name,
                chunk_engine_name="HybridChunkEngine",
                embedding_provider_name=None,
                vector_store_name=None,
                knowledge_extractor_name=None,
            )

            logger.info("Ingestion pipeline execution completed successfully.")

            return IngestionPipelineResult(
                content=content_result,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Ingestion pipeline execution failed: {e}")
            raise PipelineExecutionError(f"Ingestion pipeline execution failed: {e}") from e
