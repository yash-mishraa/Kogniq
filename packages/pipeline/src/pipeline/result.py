from dataclasses import dataclass
from datetime import datetime

from embedding.collection import EmbeddingCollection
from embedding.vectorstores.storage_result import StorageResult
from knowledge.extractors.extraction_result import KnowledgeExtractionResult

from content.chunking.collection import ChunkCollection
from content.normalized.document import NormalizedDocument


@dataclass(frozen=True)
class ContentPipelineResult:
    """Results from the content processing and chunking stage."""
    document: NormalizedDocument
    chunks: ChunkCollection


@dataclass(frozen=True)
class EmbeddingPipelineResult:
    """Results from the embedding generation and storage stage."""
    collection: EmbeddingCollection
    storage_result: StorageResult


@dataclass(frozen=True)
class KnowledgePipelineResult:
    """Results from the knowledge extraction stage."""
    extraction_result: KnowledgeExtractionResult


@dataclass(frozen=True)
class PipelineExecutionMetadata:
    """Metadata and statistics about the pipeline execution."""
    started_at: datetime
    completed_at: datetime
    total_processing_time_ms: float
    processor_name: str
    chunk_engine_name: str
    embedding_provider_name: str
    vector_store_name: str
    knowledge_extractor_name: str


@dataclass(frozen=True)
class PipelineResult:
    """Immutable result from a complete end-to-end Document Intelligence Pipeline execution."""
    content: ContentPipelineResult
    embeddings: EmbeddingPipelineResult
    knowledge: KnowledgePipelineResult
    metadata: PipelineExecutionMetadata
