from datetime import UTC, datetime

import pytest
from knowledge.extractors.exceptions import ExtractorConfigurationError
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from knowledge.extractors.provider_info import KnowledgeExtractorInfo
from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection


class FakeExtractor(AbstractKnowledgeExtractor):
    def __init__(self, extractor_id: str = "fake") -> None:
        self._info = KnowledgeExtractorInfo(
            extractor_id=extractor_id,
            extractor_name="Fake Extractor",
            version="1.0",
            provider="Fake Provider",
            supports_batch_processing=True,
            supports_streaming=False,
            maximum_chunks_per_request=100,
            maximum_tokens=8000,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )

    @property
    def info(self) -> KnowledgeExtractorInfo:
        return self._info

    def extract(self, chunks: ChunkCollection) -> KnowledgeExtractionResult:  # noqa: ARG002
        return KnowledgeExtractionResult(
            graph=KnowledgeGraph(concepts=(), relationships=()),
            extractor_id=self._info.extractor_id,
            extractor_name=self._info.extractor_name,
            version=self._info.version,
            processing_time_ms=0,
            processed_chunks=0,
            created_at=datetime.now(UTC),
        )

    def extract_batch(
        self, collections: tuple[ChunkCollection, ...]
    ) -> tuple[KnowledgeExtractionResult, ...]:
        return tuple(self.extract(c) for c in collections)


def test_extractor_info_validation() -> None:
    with pytest.raises(ExtractorConfigurationError, match="maximum_chunks_per_request must be > 0"):
        KnowledgeExtractorInfo(
            extractor_id="test",
            extractor_name="Test",
            version="1",
            provider="Test",
            supports_batch_processing=True,
            supports_streaming=True,
            maximum_chunks_per_request=0,
            maximum_tokens=1000,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )

    with pytest.raises(ExtractorConfigurationError, match="maximum_tokens must be > 0"):
        KnowledgeExtractorInfo(
            extractor_id="test",
            extractor_name="Test",
            version="1",
            provider="Test",
            supports_batch_processing=True,
            supports_streaming=True,
            maximum_chunks_per_request=10,
            maximum_tokens=0,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )


def test_fake_extractor_interface() -> None:
    extractor = FakeExtractor()
    assert extractor.info.extractor_id == "fake"
    assert extractor.extract(ChunkCollection(chunks=())).graph.concept_count == 0
