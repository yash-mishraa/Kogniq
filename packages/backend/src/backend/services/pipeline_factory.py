from unittest.mock import MagicMock

from pipeline.pipeline import DocumentIntelligencePipeline


class PipelineFactory:
    """
    Constructs instances of DocumentIntelligencePipeline.
    Today it injects fake or mocked implementations to preserve testability.
    Tomorrow it will inject real implementations bound to actual databases and LLMs.
    """

    @classmethod
    def create(cls) -> DocumentIntelligencePipeline:
        pipeline_mock = MagicMock(spec=DocumentIntelligencePipeline)

        from typing import Any

        def mock_run(handle: Any) -> MagicMock:
            result_mock = MagicMock()
            from datetime import UTC, datetime

            from embedding.collection import EmbeddingCollection
            from knowledge.graph import KnowledgeGraph
            from pipeline.result import PipelineExecutionMetadata

            from content.chunking import Chunk, ChunkMetadata, ChunkStatistics
            from content.chunking.collection import ChunkCollection

            dummy_chunk = Chunk(
                id="c1",
                document_id=handle.id,
                chunk_index=0,
                text="test chunk",
                created_at=datetime.now(UTC),
                metadata=ChunkMetadata(
                    processor="mock", document_version="v1", source="mock", checksum="123"
                ),
                statistics=ChunkStatistics(
                    character_count=10,
                    line_count=1,
                    word_count=2,
                    estimated_tokens=2,
                    processing_timestamp=datetime.now(UTC),
                    confidence=1.0,
                ),
            )

            result_mock.content.chunks = ChunkCollection(chunks=(dummy_chunk,))
            result_mock.embeddings.collection = EmbeddingCollection(embeddings=())
            result_mock.knowledge.extraction_result.graph = KnowledgeGraph(
                concepts=(), relationships=()
            )
            result_mock.metadata = PipelineExecutionMetadata(
                started_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
                total_processing_time_ms=10.0,
                processor_name="mock",
                chunk_engine_name="mock",
                embedding_provider_name="mock",
                vector_store_name="mock",
                knowledge_extractor_name="mock",
            )

            # We need a concrete NormalizedDocument to avoid SQLite failing to bind MagicMock
            from datetime import UTC, datetime

            from content.normalized.block import NormalizedBlock
            from content.normalized.document import NormalizedDocument
            from content.normalized.enums import BlockType
            from content.normalized.metadata import DocumentMetadata
            from content.normalized.page import NormalizedPage

            block = NormalizedBlock(
                block_id="b1", block_type=BlockType.PARAGRAPH, text="test", order=0
            )
            page = NormalizedPage(page_number=1, blocks=(block,))

            result_mock.content.document = NormalizedDocument(
                id=handle.id,
                title="Test Doc",
                source="mock",
                checksum="123",
                version="v1",
                pages=(page,),
                metadata=DocumentMetadata(author="test"),
                created_at=datetime.now(UTC),
            )
            return result_mock

        pipeline_mock.run.side_effect = mock_run
        return pipeline_mock
