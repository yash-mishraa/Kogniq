import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

# Ensure we can import from packages
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "learning-content" / "src"))

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.generators.summary import SummaryGenerator
from learning_content.providers.openrouter import OpenRouterTextGenerationProvider


def run_demo() -> None:
    print("=" * 60)
    print("AI-Powered Summary Generation via OpenRouter Demo")
    print("=" * 60)

    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not found.")
        print("Please set it in your .env file.")
        sys.exit(1)

    print("\n[1] Constructing Mock Data...")
    chunk_1 = Chunk(
        id="chunk-1",
        document_id="doc-123",
        chunk_index=0,
        text=(
            "Recursion is a method of solving a computational problem where "
            "the solution depends on solutions to smaller instances of the same problem."
        ),
        metadata=ChunkMetadata(
            processor="test", document_version="1.0", source="test", checksum="123"
        ),
        statistics=ChunkStatistics(
            character_count=140,
            line_count=1,
            word_count=21,
            estimated_tokens=27,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    chunk_2 = Chunk(
        id="chunk-2",
        document_id="doc-123",
        chunk_index=1,
        text=(
            "A recursive function must have a base case to terminate, "
            "otherwise it will run infinitely and cause a stack overflow."
        ),
        metadata=ChunkMetadata(
            processor="test", document_version="1.0", source="test", checksum="123"
        ),
        statistics=ChunkStatistics(
            character_count=117,
            line_count=1,
            word_count=20,
            estimated_tokens=26,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    chunks = ChunkCollection(chunks=(chunk_1, chunk_2))

    concept_1 = KnowledgeConcept(
        id="c1",
        title="Recursion",
        description="A method of solving problems by breaking them down into smaller instances.",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=KnowledgeMetadata(
            source_document="doc-123",
            source_chunk="chunk-1",
            language="en",
            confidence=1.0,
            extraction_version="1.0",
            created_by="demo",
        ),
    )
    concept_2 = KnowledgeConcept(
        id="c2",
        title="Base Case",
        description="The condition that terminates a recursive function.",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=KnowledgeMetadata(
            source_document="doc-123",
            source_chunk="chunk-2",
            language="en",
            confidence=1.0,
            extraction_version="1.0",
            created_by="demo",
        ),
    )
    rel_1 = KnowledgeRelationship(
        id="rel-1",
        source_concept="Recursion",
        target_concept="Base Case",
        relationship_type=RelationshipType.DEPENDS_ON,
        confidence=1.0,
        metadata=KnowledgeMetadata(
            source_document="doc-123",
            source_chunk="chunk-2",
            language="en",
            confidence=1.0,
            extraction_version="1.0",
            created_by="demo",
        ),
    )
    graph = KnowledgeGraph(concepts=(concept_1, concept_2), relationships=(rel_1,))

    model_name = "meta-llama/llama-3.1-8b-instruct"
    print(f"\n[2] Initializing OpenRouter Provider ({model_name})...")
    provider = OpenRouterTextGenerationProvider(api_key=api_key, model_name=model_name)

    print("\n[3] Initializing Summary Generator...")
    generator = SummaryGenerator(provider=provider)

    print("\n[4] Generating Summary...")
    start_time = time.time()
    try:
        content = generator.generate(chunks=chunks, graph=graph)
        end_time = time.time()

        latency = end_time - start_time

        print("\n[5] Generation Complete!")
        print(f"Provider:        {content.metadata.provider}")
        print(f"Model:           {content.metadata.model}")
        print(f"Prompt Version:  {content.metadata.prompt_version}")
        print(f"Generation Time: {latency:.2f} seconds")
        print(f"Characters:      {content.statistics.character_count}")
        print(f"Words:           {content.statistics.word_count}")
        print(f"Estimated Tokens:{content.statistics.estimated_tokens}")
        print("\n--- Summary Preview ---")
        print(content.body)
        print("-" * 23)
        print(f"\nMetadata: {content.metadata}")
        print(f"\nStatistics: {content.statistics}")

    except Exception as e:
        print(f"\nERROR during generation: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
