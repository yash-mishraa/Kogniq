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

        result_mock = MagicMock()
        result_mock.metadata.processor_name = "mock"
        result_mock.content.chunks.total_chunks = 1
        result_mock.embeddings.collection.embeddings = []
        result_mock.knowledge.extraction_result.graph.concept_count = 0
        result_mock.knowledge.extraction_result.graph.relationship_count = 0
        result_mock.metadata.total_processing_time_ms = 10.0

        # We need a concrete NormalizedDocument to avoid SQLite failing to bind MagicMock
        from datetime import UTC, datetime

        from content.normalized.block import NormalizedBlock
        from content.normalized.document import NormalizedDocument
        from content.normalized.enums import BlockType
        from content.normalized.metadata import DocumentMetadata
        from content.normalized.page import NormalizedPage

        block = NormalizedBlock(block_id="b1", block_type=BlockType.PARAGRAPH, text="test", order=0)
        page = NormalizedPage(page_number=1, blocks=(block,))

        result_mock.content.document = NormalizedDocument(
            id="test-doc-123",
            title="Test Doc",
            source="mock",
            checksum="123",
            version="v1",
            pages=(page,),
            metadata=DocumentMetadata(author="test"),
            created_at=datetime.now(UTC),
        )

        pipeline_mock.run.return_value = result_mock
        return pipeline_mock
