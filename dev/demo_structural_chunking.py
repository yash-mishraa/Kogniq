import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.chunking.strategies.structural import StructuralChunkStrategy
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.page import NormalizedPage


def main() -> None:
    print("Building multi-section NormalizedDocument...")
    
    blocks = [
        NormalizedBlock(
            block_id="b1", 
            block_type=BlockType.PARAGRAPH, 
            text="This is the introduction text before any headings appear.", 
            order=0
        ),
        
        NormalizedBlock(
            block_id="b2", 
            block_type=BlockType.HEADING, 
            text="Linear Algebra", 
            order=1
        ),
        NormalizedBlock(
            block_id="b3", 
            block_type=BlockType.PARAGRAPH, 
            text="Linear algebra is the branch of mathematics concerning linear equations.", 
            order=2
        ),
        
        NormalizedBlock(
            block_id="b4", 
            block_type=BlockType.HEADING, 
            text="Vectors", 
            order=3
        ),
        NormalizedBlock(
            block_id="b5", 
            block_type=BlockType.PARAGRAPH, 
            text="A vector is an element of a vector space.", 
            order=4
        ),
        NormalizedBlock(
            block_id="b6", 
            block_type=BlockType.LIST, 
            text="- Direction\n- Magnitude", 
            order=5
        ),
        
        NormalizedBlock(
            block_id="b7", 
            block_type=BlockType.HEADING, 
            text="Matrices", 
            order=6
        ),
        NormalizedBlock(
            block_id="b8", 
            block_type=BlockType.PARAGRAPH, 
            text="A matrix is a rectangular array or table of numbers.", 
            order=7
        ),
        
        NormalizedBlock(
            block_id="b9", 
            block_type=BlockType.HEADING, 
            text="Probability", 
            order=8
        ),
        NormalizedBlock(
            block_id="b10", 
            block_type=BlockType.PARAGRAPH, 
            text=(
                "Probability is the branch of mathematics concerning numerical "
                "descriptions of how likely an event is to occur."
            ), 
            order=9
        ),
        
        NormalizedBlock(
            block_id="b11", 
            block_type=BlockType.HEADING, 
            text="Bayes Rule", 
            order=10
        ),
        NormalizedBlock(
            block_id="b12", 
            block_type=BlockType.PARAGRAPH, 
            text=(
                "Bayes' theorem describes the probability of an event, "
                "based on prior knowledge of conditions."
            ), 
            order=11
        ),
    ]
    
    doc = NormalizedDocument(
        id="doc-math-1",
        title="Mathematics Fundamentals",
        pages=(NormalizedPage(page_number=1, blocks=tuple(blocks)),),
        source="demo-script",
        checksum="hash123",
        version="1.0",
        created_at=datetime.now(UTC)
    )
    
    print("Running StructuralChunkStrategy...")
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    print("-" * 32)
    print("Chunk Strategy Results")
    print(f"Total Chunks: {collection.total_chunks}")
    print("-" * 32)
    
    for chunk in collection.chunks:
        print(f"\nChunk Title : {chunk.title}")
        print(f"Index       : {chunk.chunk_index}")
        print(f"Page        : {chunk.page_number}")
        print(f"Characters  : {chunk.statistics.character_count}")
        
        preview = chunk.text.replace("\n", " | ")
        if len(preview) > 100:
            preview = preview[:97] + "..."
        print(f"Preview     : {preview}")

if __name__ == "__main__":
    main()
