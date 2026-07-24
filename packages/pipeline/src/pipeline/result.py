from dataclasses import dataclass
from datetime import datetime

from embedding.collection import EmbeddingCollection
from embedding.vectorstores.storage_result import StorageResult
from knowledge.extractors.extraction_result import KnowledgeExtractionResult

from content.chunking.collection import ChunkCollection
from content.normalized.document import NormalizedDocument


@dataclass
class ContentPipelineResult:
    document: NormalizedDocument
    chunks: ChunkCollection


@dataclass
class EmbeddingPipelineResult:
    collection: EmbeddingCollection
    storage_result: StorageResult


@dataclass
class KnowledgePipelineResult:
    extraction_result: KnowledgeExtractionResult


@dataclass
class PipelineExecutionMetadata:
    started_at: datetime
    completed_at: datetime
    total_processing_time_ms: float
    processor_name: str
    chunk_engine_name: str
    embedding_provider_name: str | None
    vector_store_name: str | None
    knowledge_extractor_name: str | None


@dataclass
class IngestionPipelineResult:
    """Result of the first half of the intelligence pipeline (parsing + chunking)."""
    content: ContentPipelineResult
    metadata: PipelineExecutionMetadata


@dataclass
class PipelineResult:
    content: ContentPipelineResult
    embeddings: EmbeddingPipelineResult
    knowledge: KnowledgePipelineResult
    metadata: PipelineExecutionMetadata
