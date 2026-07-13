import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.chunking.strategies.fixed_size import FixedSizeChunkStrategy
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.page import NormalizedPage


def main() -> None:
    print("Building NormalizedDocument...")
    
    blocks = [
        NormalizedBlock(
            block_id="b1", 
            block_type=BlockType.PARAGRAPH, 
            text="This is a preamble paragraph. It sets up the context.", 
            order=0
        ),
        NormalizedBlock(
            block_id="b2", 
            block_type=BlockType.HEADING, 
            text="First Major Section", 
            order=1
        ),
        NormalizedBlock(
            block_id="b3", 
            block_type=BlockType.PARAGRAPH, 
            text=(
                "This section discusses fixed-size boundaries. "
                "We will see how texts are broken up when limits are hit."
            ), 
            order=2
        ),
        NormalizedBlock(
            block_id="b4", 
            block_type=BlockType.PARAGRAPH, 
            text="Sometimes a paragraph is just short.", 
            order=3
        ),
        NormalizedBlock(
            block_id="b5", 
            block_type=BlockType.PARAGRAPH, 
            text=(
                "Other times, it continues discussing the first major section "
                "and introduces some advanced metrics."
            ), 
            order=4
        ),
        NormalizedBlock(
            block_id="b6", 
            block_type=BlockType.HEADING, 
            text="Second Major Section", 
            order=5
        ),
        NormalizedBlock(
            block_id="b7", 
            block_type=BlockType.PARAGRAPH, 
            text=(
                "Here is a single block that is intentionally extremely long to demonstrate "
                "how oversized blocks are handled natively without splitting. It goes on and "
                "on, continuing past the configured max limit to ensure block atomicity "
                "is maintained."
            ), 
            order=6
        ),
    ]
    
    doc = NormalizedDocument(
        id="doc-fixed-1",
        title="Fixed Chunking Rules",
        pages=(NormalizedPage(page_number=1, blocks=tuple(blocks)),),
        source="demo-script",
        checksum="hash123",
        version="1.0",
        created_at=datetime.now(UTC)
    )
    
    max_chars = 150
    print(f"Running FixedSizeChunkStrategy (max_characters={max_chars})...")
    strategy = FixedSizeChunkStrategy(max_characters=max_chars)
    collection = strategy.chunk(doc)
    
    print("-" * 32)
    print("Chunk Strategy Results")
    print(f"Configured Chunk Size: {max_chars}")
    print(f"Total Chunks: {collection.total_chunks}")
    print("-" * 32)
    
    for chunk in collection.chunks:
        print(f"\nChunk Index : {chunk.chunk_index}")
        print(f"Chunk Title : {chunk.title}")
        print(f"Section     : {chunk.section_title}")
        print(f"Page        : {chunk.page_number}")
        print(f"Characters  : {chunk.statistics.character_count}")
        
        preview = chunk.text.replace("\n", " | ")
        if len(preview) > 100:
            preview = preview[:97] + "..."
        print(f"Preview     : {preview}")

if __name__ == "__main__":
    main()
