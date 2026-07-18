from datetime import UTC, datetime
from typing import cast

import pytest
from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    AbstractPromptBuilder,
    BaseLearningGenerator,
    GenerationContext,
    GenerationMetadata,
    LearningGenerationError,
    ParsingError,
    PromptBuildingError,
)
from learning_content.metadata import LearningContentMetadata
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)
from learning_content.providers.provider_info import GeneratorInfo
from learning_content.statistics import LearningContentStatistics


class MockProvider(AbstractTextGenerationProvider):
    def __init__(self, response: str = "Mock Response") -> None:
        self._response = response
        self.last_prompt = ""
        self.call_count = 0
        self.fail_on_generate = False

    @property
    def info(self) -> TextGenerationProviderInfo:
        return TextGenerationProviderInfo(
            provider_id="mock-provider",
            provider_name="Mock",
            default_model="mock-v1",
            model_version="1.0",
            context_window=1000,
        )

    def generate(
        self, prompt: str, *, temperature: float | None = None, max_tokens: int | None = None
    ) -> str:
        if self.fail_on_generate:
            raise ValueError("Provider failure")
        self.call_count += 1
        self.last_prompt = prompt
        return self._response


class MockPromptBuilder(AbstractPromptBuilder):
    def __init__(self) -> None:
        self.fail_on_build = False
        self.call_count = 0

    def build(self, context: GenerationContext) -> str:
        if self.fail_on_build:
            raise PromptBuildingError("Prompt building failed")
        self.call_count += 1
        return "Mock Prompt"


class MockParser(AbstractContentParser):
    def __init__(self) -> None:
        self.fail_on_parse = False
        self.call_count = 0
        self.last_metadata: GenerationMetadata | None = None

    def parse(
        self, raw_text: str, context: GenerationContext, metadata: GenerationMetadata
    ) -> LearningContent:
        if self.fail_on_parse:
            raise ParsingError("Parsing failed")
        self.call_count += 1
        self.last_metadata = metadata

        return LearningContent(
            id="test-123",
            title="Test Content",
            body=raw_text,
            content_type=ContentType.SUMMARY,
            source_document_id="doc1",
            source_chunk_ids=("c1",),
            metadata=LearningContentMetadata(
                provider=metadata.provider_name,
                model=metadata.model_name,
                model_version=metadata.model_version,
                generation_version=metadata.generation_version,
                language="en",
                educational_level="unknown",
                subject="unknown",
                syllabus="unknown",
                tags=(),
                generation_id="test-gen-123",
                prompt_version=metadata.prompt_version,
                template_version="1.0",
            ),
            statistics=LearningContentStatistics(
                character_count=len(raw_text),
                word_count=len(raw_text.split()),
                estimated_tokens=10,
                processing_time_ms=metadata.generation_time_ms,
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        )


class ConcreteGenerator(BaseLearningGenerator):
    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        super().__init__(provider)
        self._prompt_builder = MockPromptBuilder()
        self._parser = MockParser()
        self.before_generate_called = 0
        self.after_generate_called = 0

    @property
    def prompt_builder(self) -> AbstractPromptBuilder:
        return self._prompt_builder

    @property
    def parser(self) -> AbstractContentParser:
        return self._parser

    @property
    def prompt_version(self) -> str:
        return "concrete-v1"

    def info(self) -> GeneratorInfo:
        return GeneratorInfo(
            generator_id="concrete",
            generator_name="Concrete",
            generator_version="1.0",
            provider_name=self._provider.info.provider_id,
            supported_content_types=(ContentType.SUMMARY,),
            maximum_chunks=10,
            maximum_tokens=1000,
            supports_batch_generation=True,
        )

    def before_generate(self, context: GenerationContext) -> None:
        self.before_generate_called += 1

    def after_generate(self, content: LearningContent) -> None:
        self.after_generate_called += 1


@pytest.fixture
def empty_context() -> tuple[ChunkCollection, KnowledgeGraph]:
    return ChunkCollection(chunks=()), KnowledgeGraph(concepts=(), relationships=())


def test_orchestration_order_and_metadata(
    empty_context: tuple[ChunkCollection, KnowledgeGraph],
) -> None:
    chunks, graph = empty_context
    provider = MockProvider()
    generator = ConcreteGenerator(provider)

    content = generator.generate(chunks, graph)

    mock_builder = cast(MockPromptBuilder, generator.prompt_builder)
    mock_parser = cast(MockParser, generator.parser)

    assert mock_builder.call_count == 1
    assert provider.call_count == 1
    assert mock_parser.call_count == 1

    assert generator.before_generate_called == 1
    assert generator.after_generate_called == 1

    # Check metadata propagation
    meta = mock_parser.last_metadata
    assert meta is not None
    assert meta.provider_name == "mock-provider"
    assert meta.model_name == "mock-v1"
    assert meta.model_version == "1.0"
    assert meta.prompt_version == "concrete-v1"
    assert meta.generation_time_ms >= 0.0

    # Ensure metadata made it into the LearningContent via parser
    assert content.metadata.provider == "mock-provider"


def test_prompt_builder_failure(empty_context: tuple[ChunkCollection, KnowledgeGraph]) -> None:
    chunks, graph = empty_context
    provider = MockProvider()
    generator = ConcreteGenerator(provider)
    mock_builder = cast(MockPromptBuilder, generator.prompt_builder)
    mock_builder.fail_on_build = True

    with pytest.raises(PromptBuildingError):
        generator.generate(chunks, graph)

    mock_parser = cast(MockParser, generator.parser)
    assert provider.call_count == 0
    assert mock_parser.call_count == 0
    assert generator.before_generate_called == 1
    assert generator.after_generate_called == 0


def test_provider_failure(empty_context: tuple[ChunkCollection, KnowledgeGraph]) -> None:
    chunks, graph = empty_context
    provider = MockProvider()
    provider.fail_on_generate = True
    generator = ConcreteGenerator(provider)

    with pytest.raises(
        LearningGenerationError, match="Failed to generate learning content: Provider failure"
    ):
        generator.generate(chunks, graph)

    mock_builder = cast(MockPromptBuilder, generator.prompt_builder)
    mock_parser = cast(MockParser, generator.parser)

    assert mock_builder.call_count == 1
    assert mock_parser.call_count == 0
    assert generator.before_generate_called == 1
    assert generator.after_generate_called == 0


def test_parser_failure(empty_context: tuple[ChunkCollection, KnowledgeGraph]) -> None:
    chunks, graph = empty_context
    provider = MockProvider()
    generator = ConcreteGenerator(provider)
    mock_parser = cast(MockParser, generator.parser)
    mock_parser.fail_on_parse = True

    with pytest.raises(ParsingError):
        generator.generate(chunks, graph)

    mock_builder = cast(MockPromptBuilder, generator.prompt_builder)
    assert mock_builder.call_count == 1
    assert provider.call_count == 1
    assert generator.before_generate_called == 1
    assert generator.after_generate_called == 0


def test_batch_generation_sequential(empty_context: tuple[ChunkCollection, KnowledgeGraph]) -> None:
    chunks, graph = empty_context
    provider = MockProvider()
    generator = ConcreteGenerator(provider)

    collections = (chunks, chunks)
    graphs = (graph, graph)

    collection = generator.generate_batch(collections, graphs)

    mock_builder = cast(MockPromptBuilder, generator.prompt_builder)
    mock_parser = cast(MockParser, generator.parser)

    assert len(collection.contents) == 2
    assert mock_builder.call_count == 2
    assert provider.call_count == 2
    assert mock_parser.call_count == 2
    assert generator.before_generate_called == 2
    assert generator.after_generate_called == 2


def test_batch_generation_mismatch() -> None:
    provider = MockProvider()
    generator = ConcreteGenerator(provider)

    with pytest.raises(LearningGenerationError, match="Mismatched collections"):
        generator.generate_batch((), (KnowledgeGraph(concepts=(), relationships=()),))
