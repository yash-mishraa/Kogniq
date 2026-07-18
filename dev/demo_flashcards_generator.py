import json
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
from learning_content.generators.flashcards.generator import FlashcardsGenerator
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
        return json.dumps(
            [
                {
                    "question": "What is Gradient Descent?",
                    "answer": (
                        "An optimization algorithm used to minimize loss "
                        "by iteratively moving in the direction of steepest descent."
                    ),
                    "difficulty": "medium",
                },
                {
                    "question": "What happens during overfitting?",
                    "answer": (
                        "The model learns the training data too well, including its noise, "
                        "leading to poor generalization on new data."
                    ),
                    "difficulty": "easy",
                },
            ],
            indent=2,
        )


if __name__ == "__main__":
    print("============================================================")
    print("Flashcards Generator Demo")
    print("============================================================")

    provider = DemoProvider()
    generator = FlashcardsGenerator(provider)

    chunks = ChunkCollection(
        chunks=(
            Chunk(
                id="chunk-1",
                document_id="ml-intro",
                chunk_index=0,
                text="Machine learning models use optimization algorithms like Gradient Descent.",
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

    print("\n[1] Generating Flashcards...")
    start = time.perf_counter()
    content = generator.generate(chunks, graph)
    end = time.perf_counter()

    print(f"\n[2] Generation Complete in {end - start:.2f}s!")
    print(f"Title: {content.title}")

    parsed_cards = json.loads(content.body)
    print(f"Total Cards: {len(parsed_cards)}")
    print(
        f"Metadata: Provider={content.metadata.provider}, "
        f"PromptVersion={content.metadata.prompt_version}"
    )

    print("\n[3] Generated Structured Content:\n")
    for i, card in enumerate(parsed_cards, 1):
        print(f"--- Card {i} [{card.get('difficulty', 'unknown').upper()}] ---")
        print(f"Q: {card.get('question')}")
        print(f"A: {card.get('answer')}\n")
