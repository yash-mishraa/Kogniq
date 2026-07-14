from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add the source directories to sys.path so the demo can run without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from knowledge.extractors.gemini.extractor import GeminiKnowledgeExtractor

from datetime import datetime, timezone
from content.chunking.chunk import Chunk
from content.chunking.statistics import ChunkStatistics
from content.chunking.metadata import ChunkMetadata
from content.chunking.collection import ChunkCollection


def main() -> None:
    load_dotenv(override=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Skipping extraction demo: GEMINI_API_KEY not found in environment.")
        return

    print("Initializing Gemini Knowledge Extractor...")
    extractor = GeminiKnowledgeExtractor(api_key=api_key, model_name="gemini-2.0-flash")

    print(f"Extractor registered: {extractor.info.extractor_id}")

    chunk = Chunk(
        id="chunk_1",
        text=(
            "Photosynthesis is a process used by plants to convert light energy "
            "into chemical energy. Cellular respiration is a set of metabolic "
            "reactions that convert biochemical energy from nutrients into "
            "adenosine triphosphate (ATP). Photosynthesis provides the glucose "
            "used in cellular respiration."
        ),
        document_id="doc_bio_1",
        chunk_index=1,
        metadata=ChunkMetadata(
            processor="test_processor",
            document_version="v1",
            source="test",
            checksum="fake_hash",
        ),
        statistics=ChunkStatistics(
            character_count=100, 
            word_count=20, 
            estimated_tokens=15,
            line_count=4,
            processing_timestamp=datetime.now(timezone.utc),
            confidence=1.0,
        ),
        created_at=datetime.now(timezone.utc),
    )
    collection = ChunkCollection(chunks=(chunk,))

    print("\nStarting extraction...")
    result = extractor.extract(collection)

    print(f"\nExtraction completed in {result.processing_time_ms:.2f} ms")
    
    graph = result.graph
    print(f"Concepts extracted: {graph.concept_count}")
    for concept in graph.concepts:
        print(f"  - [{concept.id}] {concept.title} (Aliases: {', '.join(concept.aliases)})")

    print(f"\nRelationships extracted: {graph.relationship_count}")
    for rel in graph.relationships:
        print(f"  - [{rel.relationship_type.name}] {rel.source_concept} -> {rel.target_concept}")


if __name__ == "__main__":
    main()
