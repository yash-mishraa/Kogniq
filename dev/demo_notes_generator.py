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
from learning_content.generators.notes.generator import NotesGenerator
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
            "# Machine Learning Basics\n\n"
            "## Core Concepts\n"
            "- **Supervised Learning**: Training on labeled data.\n"
            "- **Unsupervised Learning**: Discovering patterns in unlabeled data.\n\n"
            "### Important Facts\n"
            "- Overfitting happens when a model learns the training data too well.\n\n"
            "### Key Definitions\n"
            "- **Gradient Descent**: Optimization algorithm to minimize loss.\n\n"
            "### Exam Tips\n"
            "- Remember the difference between L1 and L2 regularization.\n\n"
            "### Common Mistakes\n"
            "- Not scaling features before applying gradient descent.\n"
        )


if __name__ == "__main__":
    print("============================================================")
    print("Notes Generator Demo")
    print("============================================================")

    provider = DemoProvider()
    generator = NotesGenerator(provider)

    chunks = ChunkCollection(
        chunks=(
            Chunk(
                id="chunk-1",
                document_id="ml-intro",
                chunk_index=0,
                text="Machine learning consists of supervised and unsupervised approaches.",
                metadata=ChunkMetadata(
                    processor="txt", document_version="1", source="demo", checksum="123"
                ),
                statistics=ChunkStatistics(
                    character_count=66,
                    line_count=1,
                    word_count=9,
                    estimated_tokens=12,
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
                title="Supervised Learning",
                description="Learning with labels",
                concept_type=ConceptType.PRINCIPLE,
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

    print("\n[1] Generating Notes...")
    start = time.perf_counter()
    content = generator.generate(chunks, graph)
    end = time.perf_counter()

    print(f"\n[2] Generation Complete in {end - start:.2f}s!")
    print(f"Title: {content.title}")
    print(
        f"Stats: {content.statistics.word_count} words, "
        f"{content.statistics.character_count} chars"
    )
    print(
        f"Metadata: Provider={content.metadata.provider}, "
        f"PromptVersion={content.metadata.prompt_version}"
    )
    print("\n[3] Generated Content:\n")
    print(content.body)
