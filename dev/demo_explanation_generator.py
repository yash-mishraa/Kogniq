import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "shared" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "learning-content" / "src"))

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.generators.explanation.generator import ExplanationGenerator
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class DemoProvider(AbstractTextGenerationProvider):
    @property
    def info(self) -> TextGenerationProviderInfo:
        return TextGenerationProviderInfo(
            provider_id="demo-provider",
            provider_name="Demo",
            default_model="demo-model",
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
        return (
            "# Concept\n"
            "Gradient Descent is the engine that powers almost all of modern machine learning.\n\n"
            "## Why It Matters\n"
            "Gradient descent is the engine that powers almost all of modern machine learning.\n\n"
            "## Intuition\n"
            "Imagine you are blindfolded on a mountain and want to reach the bottom. "
            "You feel the slope with your feet and take a step in the steepest downward "
            "direction.\n\n"
            "## Detailed Explanation\n"
            "It calculates the gradient of the loss function with respect to the "
            "parameters, and updates the parameters in the opposite direction.\n\n"
            "## Example\n"
            "If predicting house prices, the loss is the error between predictions "
            "and actual prices.\n\n"
            "## Common Mistakes\n"
            "Setting the learning rate too high, which causes divergence.\n\n"
            "## Related Concepts\n"
            "Backpropagation, Loss Functions, Learning Rates.\n\n"
            "## Key Takeaways\n"
            "- It minimizes the loss function.\n"
            "- It relies on gradients.\n"
        )


if __name__ == "__main__":
    print("============================================================")
    print("Explanation Generator Demo")
    print("============================================================")

    provider = DemoProvider()
    generator = ExplanationGenerator(provider)

    chunks = ChunkCollection(
        chunks=(
            Chunk(
                id="chunk-1",
                document_id="ml-intro",
                chunk_index=0,
                text="Gradient descent minimizes the loss.",
                metadata=ChunkMetadata(
                    processor="txt", document_version="1", source="demo", checksum="123"
                ),
                statistics=ChunkStatistics(
                    character_count=70,
                    line_count=1,
                    word_count=10,
                    estimated_tokens=13,
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
                title="Gradient Descent",
                description="Optimization algorithm",
                concept_type=ConceptType.ALGORITHM,
                aliases=(),
                metadata=KnowledgeMetadata(
                    source_document="ml-intro",
                    source_chunk="chunk-1",
                    language="en",
                    confidence=1.0,
                    extraction_version="1.0",
                    created_by="demo",
                ),
            ),
        ),
        relationships=(),
    )

    print("\n[1] Generating Explanation...")
    start = time.perf_counter()
    content = generator.generate(chunks, graph)
    end = time.perf_counter()

    print(f"\n[2] Generation Complete in {end - start:.2f}s!")
    print(f"Title: {content.title}")

    print(
        f"Metadata: Provider={content.metadata.provider}, "
        f"PromptVersion={content.metadata.prompt_version}"
    )

    stats = content.statistics
    print(f"Statistics: Words={stats.word_count}, Headings={stats.heading_count}")

    print("\n[3] Generated Explanation:\n")
    print(content.body)
