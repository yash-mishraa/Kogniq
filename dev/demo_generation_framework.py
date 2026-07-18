import sys
from pathlib import Path

# Setup path so we can import workspace packages
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "shared" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "learning-content" / "src"))

import time
from datetime import UTC, datetime

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.generators.summary.generator import SummaryGenerator
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)

print("=" * 60)
print("Learning Generation Framework Demo")
print("=" * 60)


class DemoProvider(AbstractTextGenerationProvider):
    """A fake provider that logs when it is called."""

    @property
    def info(self) -> TextGenerationProviderInfo:
        return TextGenerationProviderInfo(
            provider_id="demo-framework",
            provider_name="Framework Demo",
            default_model="demo-v1",
            model_version="1.0",
            context_window=1000,
        )

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        _ = (prompt, temperature, max_tokens)
        print("[DemoProvider] Received prompt.")
        time.sleep(0.5)  # Simulate latency
        print("[DemoProvider] Generating response...")
        return "This is a framework-generated summary demonstrating orchestration."


print("\n[1] Constructing Generator Pipeline...")
provider = DemoProvider()
generator = SummaryGenerator(provider)

print("    Generator:", generator.info().generator_name)
print("    Provider: ", generator.info().provider_name)
print("    Builder:  ", type(generator.prompt_builder).__name__)
print("    Parser:   ", type(generator.parser).__name__)

print("\n[2] Setting up Mock Data...")
chunks = ChunkCollection(
    chunks=(
        Chunk(
            id="demo-chunk",
            document_id="doc1",
            chunk_index=0,
            text="The framework handles orchestration, while the builder handles the prompt.",
            metadata=ChunkMetadata(
                processor="txt", document_version="1", source="demo", checksum="1"
            ),
            statistics=ChunkStatistics(
                character_count=74,
                line_count=1,
                word_count=11,
                estimated_tokens=15,
                processing_timestamp=datetime.now(UTC),
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        ),
    )
)

graph = KnowledgeGraph(
    concepts=(
        KnowledgeConcept(
            id="c1",
            title="Framework",
            description="The orchestration engine",
            concept_type=ConceptType.PRINCIPLE,
            aliases=(),
            metadata=KnowledgeMetadata(
                source_document="demo",
                source_chunk="c1",
                language="en",
                confidence=1.0,
                extraction_version="1.0",
                created_by="demo_script",
            ),
        ),
        KnowledgeConcept(
            id="c2",
            title="Builder",
            description="The prompt creator",
            concept_type=ConceptType.PRINCIPLE,
            aliases=(),
            metadata=KnowledgeMetadata(
                source_document="demo",
                source_chunk="c1",
                language="en",
                confidence=1.0,
                extraction_version="1.0",
                created_by="demo_script",
            ),
        ),
    ),
    relationships=(
        KnowledgeRelationship(
            id="r1",
            source_concept="c1",
            target_concept="c2",
            relationship_type=RelationshipType.DEPENDS_ON,
            confidence=1.0,
            metadata=KnowledgeMetadata(
                source_document="demo",
                source_chunk="c1",
                language="en",
                confidence=1.0,
                extraction_version="1.0",
                created_by="demo_script",
            ),
        ),
    ),
)

print("\n[3] Executing generation...")
start = time.perf_counter()
content = generator.generate(chunks, graph)
end = time.perf_counter()

print(f"\n[4] Generation Complete in {end - start:.2f}s!")
print(f"    Content Type: {content.content_type.name}")
print(f"    Title: {content.title}")
print(f"    Body: {content.body}")
print(f"    Processing Time (ms): {content.statistics.processing_time_ms:.2f}")
print(f"    Prompt Version: {content.metadata.prompt_version}")

print("\nFramework Orchestration Successful.")
