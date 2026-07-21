import logging
import time
from datetime import UTC, datetime

from embedding.providers.interfaces import AbstractEmbeddingProvider
from embedding.vectorstores.interfaces import AbstractVectorStore
from knowledge.extractors.interfaces import AbstractKnowledgeExtractor

from content.chunking.engine import HybridChunkEngine
from content.plugins.registry import ProcessorRegistry
from content.resource.handle import ResourceHandle

from .exceptions import PipelineExecutionError
from .result import (
    ContentPipelineResult,
    EmbeddingPipelineResult,
    KnowledgePipelineResult,
    PipelineExecutionMetadata,
    PipelineResult,
)

logger = logging.getLogger(__name__)


class DocumentIntelligencePipeline:
    """
    Orchestration layer that connects bounded contexts into an end-to-end pipeline.
    """

    def __init__(
        self,
        processor_registry: ProcessorRegistry,
        chunk_engine: HybridChunkEngine,
        embedding_provider: AbstractEmbeddingProvider,
        vector_store: AbstractVectorStore,
        knowledge_extractor: AbstractKnowledgeExtractor,
    ) -> None:
        self.processor_registry = processor_registry
        self.chunk_engine = chunk_engine
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.knowledge_extractor = knowledge_extractor

    def run(self, handle: ResourceHandle) -> PipelineResult:
        """
        Executes the end-to-end document intelligence pipeline for a given resource.
        """
        start_time = time.perf_counter()
        started_at = datetime.now(UTC)

        logger.info(f"Starting pipeline execution for resource: {handle.id}")

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

            # 3. Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self.embedding_provider.generate_batch(chunks)
            logger.info(f"Generated {len(embeddings.embeddings)} embeddings.")

            # 4. Store embeddings
            logger.info("Storing embeddings in vector store...")
            storage_result = self.vector_store.store_batch(embeddings)
            logger.info(f"Stored {storage_result.stored_count} embeddings.")

            embedding_result = EmbeddingPipelineResult(
                collection=embeddings,
                storage_result=storage_result,
            )

            # 5. Extract Knowledge Graph
            logger.info("Extracting knowledge graph...")
            knowledge = self.knowledge_extractor.extract(chunks)
            logger.info(
                f"Extracted {knowledge.graph.concept_count} concepts and "
                f"{knowledge.graph.relationship_count} relationships."
            )

            knowledge_result = KnowledgePipelineResult(
                extraction_result=knowledge,
            )

            completed_at = datetime.now(UTC)
            end_time = time.perf_counter()

            metadata = PipelineExecutionMetadata(
                started_at=started_at,
                completed_at=completed_at,
                total_processing_time_ms=(end_time - start_time) * 1000,
                processor_name=processor.processor_info.name,
                chunk_engine_name="HybridChunkEngine",
                embedding_provider_name=self.embedding_provider.info.provider_name,
                vector_store_name=self.vector_store.info.store_name,
                knowledge_extractor_name=self.knowledge_extractor.info.extractor_name,
            )

            logger.info("Pipeline execution completed successfully.")

            return PipelineResult(
                content=content_result,
                embeddings=embedding_result,
                knowledge=knowledge_result,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise PipelineExecutionError(f"Pipeline execution failed: {e}") from e
