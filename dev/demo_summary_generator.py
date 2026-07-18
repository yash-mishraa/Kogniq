import sys
from pathlib import Path

# Add workspace packages to python path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "learning-content" / "src"))

from datetime import UTC, datetime

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.generators.summary import SummaryGenerator
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class DemoTextGenerationProvider(AbstractTextGenerationProvider):
    @property
    def info(self) -> TextGenerationProviderInfo:
        return TextGenerationProviderInfo(
            provider_id="demo-provider",
            provider_name="Demo Provider",
            default_model="demo-model-v1",
            model_version="1.0",
            context_window=4096,
        )

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,  # noqa: ARG002
        max_tokens: int | None = None,  # noqa: ARG002
    ) -> str:
        print("\n" + "=" * 40)
        print("PROMPT RECEIVED BY PROVIDER:")
        print("-" * 40)
        print(prompt)
        print("=" * 40 + "\n")

        return (
            "Machine learning enables systems to learn from data. "
            "Linear regression is a foundational model predicting continuous values, "
            "while gradient descent optimizes these models by minimizing error."
        )


def run_demo() -> None:
    print("Initializing Fake Chunks...")

    meta = ChunkMetadata(processor="demo", document_version="1.0", source="demo", checksum="123")
    stats = ChunkStatistics(
        character_count=100,
        line_count=1,
        word_count=20,
        estimated_tokens=26,
        processing_timestamp=datetime.now(UTC),
        confidence=1.0,
    )
    now = datetime.now(UTC)

    chunks = ChunkCollection(
        chunks=(
            Chunk(
                id="chunk-1",
                document_id="demo-doc",
                chunk_index=0,
                text=(
                    "Machine learning is a field of study that gives computers the ability "
                    "to learn without being explicitly programmed."
                ),
                metadata=meta,
                statistics=stats,
                created_at=now,
            ),
            Chunk(
                id="chunk-2",
                document_id="demo-doc",
                chunk_index=1,
                text=(
                    "Linear regression is a linear approach to modelling the relationship "
                    "between a scalar response and one or more explanatory variables."
                ),
                metadata=meta,
                statistics=stats,
                created_at=now,
            ),
            Chunk(
                id="chunk-3",
                document_id="demo-doc",
                chunk_index=2,
                text=(
                    "Gradient descent is a first-order iterative optimization algorithm "
                    "for finding a local minimum of a differentiable function."
                ),
                metadata=meta,
                statistics=stats,
                created_at=now,
            ),
        ),
    )

    k_meta = KnowledgeMetadata(
        source_document="demo-doc",
        source_chunk="chunk-1",
        language="en",
        confidence=1.0,
        extraction_version="1.0",
        created_by="demo",
    )

    print("Initializing Fake Knowledge Graph...")
    graph = KnowledgeGraph(
        concepts=(
            KnowledgeConcept(
                id="c1",
                title="Machine Learning",
                description="Study of algorithms that learn from data",
                concept_type=ConceptType.THEORY,
                aliases=("ML",),
                metadata=k_meta,
            ),
            KnowledgeConcept(
                id="c2",
                title="Linear Regression",
                description="Linear approach for modeling relationships",
                concept_type=ConceptType.ALGORITHM,
                aliases=(),
                metadata=k_meta,
            ),
            KnowledgeConcept(
                id="c3",
                title="Gradient Descent",
                description="Optimization algorithm for finding minimum",
                concept_type=ConceptType.ALGORITHM,
                aliases=("GD",),
                metadata=k_meta,
            ),
        ),
        relationships=(
            KnowledgeRelationship(
                id="r1",
                source_concept="c1",
                target_concept="c2",
                relationship_type=RelationshipType.RELATED_TO,
                confidence=1.0,
                metadata=k_meta,
            ),
            KnowledgeRelationship(
                id="r2",
                source_concept="c2",
                target_concept="c3",
                relationship_type=RelationshipType.USES,
                confidence=1.0,
                metadata=k_meta,
            ),
        ),
    )

    print("Initializing Summary Generator...")
    provider = DemoTextGenerationProvider()
    generator = SummaryGenerator(provider=provider)

    print("Generating Summary...\n")
    content = generator.generate(chunks, graph)

    print("\n" + "=" * 40)
    print("GENERATED SUMMARY CONTENT:")
    print("-" * 40)
    print(f"Title: {content.title}")
    print(f"Type:  {content.content_type.name}")
    print(f"Body:\n{content.body}")
    print("-" * 40)
    print("METADATA:")
    print(f"Provider:   {content.metadata.provider}")
    print(f"Model:      {content.metadata.model}")
    print("-" * 40)
    print("STATISTICS:")
    print(f"Word Count: {content.statistics.word_count}")
    print(f"Tokens:     {content.statistics.estimated_tokens}")
    print(f"Confidence: {content.statistics.confidence}")
    print("=" * 40)


if __name__ == "__main__":
    run_demo()
