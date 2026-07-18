"""
Developer demo for the Learning Content Generation bounded context.
Demonstrates the provider-agnostic domain models and interfaces.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

# Setup paths for editable installs in a monorepo
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "shared" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "learning-content" / "src"))

from unittest.mock import MagicMock

from knowledge.graph import KnowledgeGraph

from content.chunking import Chunk, ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.metadata import LearningContentMetadata
from learning_content.providers.interfaces import AbstractLearningGenerator
from learning_content.providers.provider_info import GeneratorInfo
from learning_content.providers.registry import LearningGeneratorRegistry
from learning_content.statistics import LearningContentStatistics


class DemoLearningGenerator(AbstractLearningGenerator):
    """A fake generator for demonstration purposes."""

    def info(self) -> GeneratorInfo:
        return GeneratorInfo(
            generator_id="demo-gen",
            generator_name="Demo Generator",
            generator_version="1.0",
            provider_name="Demo Provider",
            supported_content_types=(ContentType.SUMMARY, ContentType.NOTES),
            maximum_chunks=50,
            maximum_tokens=8192,
            supports_batch_generation=True,
        )

    def generate(self, chunks: ChunkCollection, graph: KnowledgeGraph) -> LearningContent:
        _ = graph  # Unused
        return LearningContent(
            id="demo-content-1",
            source_document_id=chunks.chunks[0].document_id if chunks.chunks else "unknown",
            source_chunk_ids=tuple(c.id for c in chunks.chunks),
            content_type=ContentType.SUMMARY,
            title="Demo Generated Summary",
            body="This is a summary generated purely in the domain layer. No LLMs were called.",
            metadata=LearningContentMetadata(
                provider="Demo Provider",
                model="demo-model",
                model_version="1.0",
                generation_version="1.0",
                language="en",
                educational_level="all",
                subject="demonstration",
                syllabus="none",
                tags=("demo", "test"),
            ),
            statistics=LearningContentStatistics(
                character_count=82,
                word_count=13,
                estimated_tokens=15,
                processing_time_ms=5.0,
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        )

    def generate_batch(
        self, collections: tuple[ChunkCollection, ...], graphs: tuple[KnowledgeGraph, ...]
    ) -> LearningContentCollection:
        return LearningContentCollection(
            contents=tuple(self.generate(c, g) for c, g in zip(collections, graphs, strict=True))
        )


def main() -> None:
    print("\n[Learning Content Generation Demo]\n")

    # 1. Setup Fake Data
    chunk_mock = MagicMock(spec=Chunk)
    chunk_mock.id = "chunk-abc"
    chunk_mock.document_id = "doc-123"

    chunks = ChunkCollection(chunks=(chunk_mock,))
    graph = MagicMock(spec=KnowledgeGraph)

    # 2. Setup Registry and Generator
    registry = LearningGeneratorRegistry()
    generator = DemoLearningGenerator()
    registry.register(generator)

    print(f"Registered Generators: {registry.generator_count()}")
    info = registry.available_generators()[0]
    print(f"Using Generator: {info.generator_name} (v{info.generator_version})\n")

    # 3. Generate Content
    print("Generating learning content...")
    content = generator.generate(chunks, graph)

    # 4. Print Results
    print("\n--- Generated Content ---")
    print(f"Title: {content.title}")
    print(f"Type:  {content.content_type.name}")
    print(f"Body:  {content.body}")
    print("\n--- Statistics ---")
    print(f"Words:  {content.statistics.word_count}")
    print(f"Tokens: {content.statistics.estimated_tokens}")
    print("-------------------------\n")


if __name__ == "__main__":
    main()
