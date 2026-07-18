import pytest
from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.providers.interfaces import AbstractLearningGenerator
from learning_content.providers.provider_info import GeneratorInfo
from learning_content.providers.registry import LearningGeneratorRegistry
from learning_content.providers.registry_exceptions import (
    GeneratorNotFoundError,
    GeneratorRegistrationError,
)


class FakeLearningGenerator(AbstractLearningGenerator):
    def info(self) -> GeneratorInfo:
        return GeneratorInfo(
            generator_id="fake-gen",
            generator_name="Fake Generator",
            generator_version="1.0",
            provider_name="Fake Provider",
            supported_content_types=(ContentType.SUMMARY,),
            maximum_chunks=10,
            maximum_tokens=1000,
            supports_batch_generation=False,
        )

    def generate(self, chunks: ChunkCollection, graph: KnowledgeGraph) -> LearningContent:
        raise NotImplementedError

    def generate_batch(
        self, collections: tuple[ChunkCollection, ...], graphs: tuple[KnowledgeGraph, ...]
    ) -> LearningContentCollection:
        raise NotImplementedError


class AnotherFakeLearningGenerator(FakeLearningGenerator):
    def info(self) -> GeneratorInfo:
        # We need to recreate it to change the ID because it's immutable
        from learning_content.enums import ContentType
        from learning_content.providers.provider_info import GeneratorInfo

        return GeneratorInfo(
            generator_id="another-gen",
            generator_name="Another Generator",
            generator_version="1.0",
            provider_name="Fake Provider",
            supported_content_types=(ContentType.QUIZ,),
            maximum_chunks=10,
            maximum_tokens=1000,
            supports_batch_generation=False,
        )


def test_registry_registration() -> None:
    registry = LearningGeneratorRegistry()
    gen1 = FakeLearningGenerator()
    gen2 = AnotherFakeLearningGenerator()

    registry.register(gen1)
    registry.register(gen2)

    assert registry.generator_count() == 2
    assert registry.has_generator("fake-gen")
    assert registry.has_generator("another-gen")


def test_registry_duplicate_registration() -> None:
    registry = LearningGeneratorRegistry()
    gen1 = FakeLearningGenerator()
    registry.register(gen1)

    with pytest.raises(GeneratorRegistrationError, match="is already registered"):
        registry.register(gen1)


def test_registry_generator_for_id() -> None:
    registry = LearningGeneratorRegistry()
    gen1 = FakeLearningGenerator()
    registry.register(gen1)

    retrieved = registry.generator_for_id("fake-gen")
    assert retrieved is gen1

    with pytest.raises(GeneratorNotFoundError, match="No generator found for id"):
        registry.generator_for_id("non-existent")


def test_registry_available_generators() -> None:
    registry = LearningGeneratorRegistry()
    gen1 = FakeLearningGenerator()
    registry.register(gen1)

    infos = registry.available_generators()
    assert len(infos) == 1
    assert infos[0].generator_id == "fake-gen"
