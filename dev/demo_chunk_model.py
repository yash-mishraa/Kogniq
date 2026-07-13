import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.chunking import (
    Chunk,
    ChunkCollection,
    ChunkMetadata,
    ChunkStatistics,
)


def main() -> None:
    print("Constructing chunk models manually...")
    
    metadata = ChunkMetadata(
        processor="markdown",
        document_version="v1.0",
        source="demo.md",
        checksum="12345abc",
        language="en",
    )
    
    created_at = datetime.now(UTC)
    
    chunk1 = Chunk(
        id="chunk-001",
        document_id="doc-demo-1",
        chunk_index=0,
        text="This is the first paragraph of our demo document. It introduces the chunk model.",
        title="Demo Document",
        section_title="Introduction",
        page_number=1,
        metadata=metadata,
        statistics=ChunkStatistics(
            character_count=80,
            line_count=1,
            word_count=14,
            estimated_tokens=18,
            processing_timestamp=created_at,
            confidence=0.99
        ),
        created_at=created_at,
    )
    
    chunk2 = Chunk(
        id="chunk-002",
        document_id="doc-demo-1",
        chunk_index=1,
        text=(
            "Chunks represent discrete semantic units of text. "
            "They are immutable and infrastructure agnostic."
        ),
        title="Demo Document",
        section_title="Architecture",
        page_number=1,
        metadata=metadata,
        statistics=ChunkStatistics(
            character_count=93,
            line_count=1,
            word_count=13,
            estimated_tokens=19,
            processing_timestamp=created_at,
            confidence=0.99
        ),
        created_at=created_at,
    )
    
    collection = ChunkCollection(chunks=(chunk1, chunk2))
    
    print("-" * 32)
    print("Chunk Collection Summary")
    print(f"Total Chunks     : {collection.total_chunks}")
    print(f"Total Characters : {collection.total_characters}")
    print(f"Total Words      : {collection.total_words}")
    print(f"Estimated Tokens : {collection.total_estimated_tokens}")
    print("-" * 32)
    
    print("\nSample Chunk 1:")
    print(f"ID       : {chunk1.id}")
    print(f"Doc ID   : {chunk1.document_id}")
    print(f"Section  : {chunk1.section_title}")
    print(f"Text     : {chunk1.text}")
    print(f"Metadata : processor={chunk1.metadata.processor}, language={chunk1.metadata.language}")
    
    print("\nSample Chunk 2:")
    print(f"ID       : {chunk2.id}")
    print(f"Doc ID   : {chunk2.document_id}")
    print(f"Section  : {chunk2.section_title}")
    print(f"Text     : {chunk2.text}")
    print(f"Metadata : processor={chunk2.metadata.processor}, language={chunk2.metadata.language}")

if __name__ == "__main__":
    main()
