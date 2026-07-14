import pytest
from knowledge.extractors.registry import KnowledgeExtractorRegistry
from knowledge.extractors.registry_exceptions import DuplicateExtractorError, ExtractorNotFoundError

from .test_extractor_interface import FakeExtractor


def test_registry_registration() -> None:
    registry = KnowledgeExtractorRegistry()
    extractor1 = FakeExtractor(extractor_id="ext_1")
    extractor2 = FakeExtractor(extractor_id="ext_2")
    
    registry.register(extractor1)
    registry.register(extractor2)
    
    assert registry.extractor_count == 2
    assert registry.has_extractor("ext_1")
    assert registry.has_extractor("ext_2")
    
    assert registry.extractor("ext_1") is extractor1
    
    available = registry.available_extractors()
    assert len(available) == 2
    assert "ext_1" in available
    assert "ext_2" in available


def test_registry_duplicate_registration_raises_error() -> None:
    registry = KnowledgeExtractorRegistry()
    extractor1 = FakeExtractor(extractor_id="ext_1")
    extractor2 = FakeExtractor(extractor_id="ext_1")  # duplicate ID
    
    registry.register(extractor1)
    with pytest.raises(DuplicateExtractorError, match="Extractor 'ext_1' is already registered"):
        registry.register(extractor2)


def test_registry_missing_extractor_raises_error() -> None:
    registry = KnowledgeExtractorRegistry()
    with pytest.raises(ExtractorNotFoundError, match="Extractor 'ext_missing' is not registered"):
        registry.extractor("ext_missing")
