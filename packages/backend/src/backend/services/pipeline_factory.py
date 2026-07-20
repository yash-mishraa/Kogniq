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

        pipeline_mock.run.return_value = result_mock
        return pipeline_mock
