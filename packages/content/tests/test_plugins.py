import pytest

from content.domain import LearningResource, ResourceType
from content.plugins import (
    AbstractContentProcessor,
    DuplicateProcessorError,
    InvalidProcessorError,
    ProcessorInfo,
    ProcessorNotFoundError,
    ProcessorRegistry,
)


class MockPDFProcessor(AbstractContentProcessor):
    @property
    def processor_info(self) -> ProcessorInfo:
        return ProcessorInfo(
            name="pdf",
            version="1.0",
            supported_extensions=("pdf",),
            supported_mime_types=("application/pdf",),
            description="Mock PDF Processor",
        )

    def process(self, resource: LearningResource) -> str:
        return "pdf text"


class MockMarkdownProcessor(AbstractContentProcessor):
    @property
    def processor_info(self) -> ProcessorInfo:
        return ProcessorInfo(
            name="md",
            version="1.0",
            supported_extensions=("md", "markdown"),
            supported_mime_types=("text/markdown",),
            description="Mock Markdown Processor",
        )

    def process(self, resource: LearningResource) -> str:
        return "md text"


class InvalidMockProcessor:
    pass


@pytest.fixture
def registry() -> ProcessorRegistry:
    return ProcessorRegistry()


@pytest.fixture
def resource() -> LearningResource:
    return LearningResource(title="T", resource_type=ResourceType.PDF, source="s", checksum="c")


def test_successful_registration(registry: ProcessorRegistry) -> None:
    proc = MockPDFProcessor()
    registry.register(proc)
    assert len(registry) == 1
    assert "pdf" in registry


def test_duplicate_processor_name(registry: ProcessorRegistry) -> None:
    proc = MockPDFProcessor()
    registry.register(proc)
    with pytest.raises(DuplicateProcessorError, match="already registered"):
        registry.register(proc)


def test_duplicate_extension(registry: ProcessorRegistry) -> None:
    class ConflictProcessor(AbstractContentProcessor):
        @property
        def processor_info(self) -> ProcessorInfo:
            return ProcessorInfo(
                name="pdf2",
                version="1.0",
                supported_extensions=("pdf",),
                supported_mime_types=("application/other",),
                description="conflict",
            )

        def process(self, resource: LearningResource) -> str:
            return ""

    registry.register(MockPDFProcessor())
    with pytest.raises(DuplicateProcessorError, match="Extension 'pdf' is already registered"):
        registry.register(ConflictProcessor())


def test_duplicate_mime_type(registry: ProcessorRegistry) -> None:
    class ConflictProcessor(AbstractContentProcessor):
        @property
        def processor_info(self) -> ProcessorInfo:
            return ProcessorInfo(
                name="pdf3",
                version="1.0",
                supported_extensions=("other",),
                supported_mime_types=("application/pdf",),
                description="conflict",
            )

        def process(self, resource: LearningResource) -> str:
            return ""

    registry.register(MockPDFProcessor())
    with pytest.raises(
        DuplicateProcessorError, match="MIME type 'application/pdf' is already registered"
    ):
        registry.register(ConflictProcessor())


def test_invalid_processor_registration(registry: ProcessorRegistry) -> None:
    with pytest.raises(InvalidProcessorError):
        registry.register(InvalidMockProcessor())  # type: ignore


def test_unregister(registry: ProcessorRegistry) -> None:
    proc = MockPDFProcessor()
    registry.register(proc)
    assert "pdf" in registry
    registry.unregister("pdf")
    assert "pdf" not in registry
    assert len(registry) == 0
    with pytest.raises(ProcessorNotFoundError):
        registry.get_by_extension("pdf")


def test_unregister_not_found(registry: ProcessorRegistry) -> None:
    with pytest.raises(ProcessorNotFoundError):
        registry.unregister("nonexistent")


def test_lookup_by_extension(registry: ProcessorRegistry) -> None:
    proc = MockPDFProcessor()
    registry.register(proc)
    found = registry.get_by_extension("pdf")
    assert found is proc
    with pytest.raises(ProcessorNotFoundError):
        registry.get_by_extension("txt")


def test_lookup_by_mime_type(registry: ProcessorRegistry) -> None:
    proc = MockPDFProcessor()
    registry.register(proc)
    found = registry.get_by_mime_type("application/pdf")
    assert found is proc
    with pytest.raises(ProcessorNotFoundError):
        registry.get_by_mime_type("text/plain")


def test_registry_iteration_and_listing(registry: ProcessorRegistry) -> None:
    p1 = MockPDFProcessor()
    p2 = MockMarkdownProcessor()
    registry.register(p1)
    registry.register(p2)

    procs = registry.list_processors()
    assert len(procs) == 2
    assert p1 in procs
    assert p2 in procs

    iterated = list(registry)
    assert len(iterated) == 2
    assert p1 in iterated
    assert p2 in iterated
