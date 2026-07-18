import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.chunking.engine import HybridChunkEngine
from content.chunking.strategies.fixed_size import FixedSizeChunkStrategy
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.page import NormalizedPage


def print_results(doc_name: str, engine: HybridChunkEngine, doc: NormalizedDocument) -> None:
    collection = engine.chunk(doc)
    print("-" * 40)
    print(f"Results for {doc_name}")
    print(f"Selected Strategy : {engine.last_selected_strategy}")
    print(f"Total Chunks      : {collection.total_chunks}")
    print("-" * 40)

    for chunk in collection.chunks:
        print(f"\nChunk Index : {chunk.chunk_index}")
        print(f"Title       : {chunk.title}")
        print(f"Characters  : {chunk.statistics.character_count}")
        preview = chunk.text.replace("\n", " | ")
        if len(preview) > 80:
            preview = preview[:77] + "..."
        print(f"Preview     : {preview}")
    print("\n")


def main() -> None:
    # Inject a fixed strategy with a small limit so we can easily see it split
    engine = HybridChunkEngine(fixed_strategy=FixedSizeChunkStrategy(max_characters=150))

    blocks_a = [
        NormalizedBlock(
            block_id="a1",
            block_type=BlockType.PARAGRAPH,
            text="This is a document with structure.",
            order=0,
        ),
        NormalizedBlock(block_id="a2", block_type=BlockType.HEADING, text="Chapter 1", order=1),
        NormalizedBlock(
            block_id="a3",
            block_type=BlockType.PARAGRAPH,
            text="The first chapter discusses structural chunking.",
            order=2,
        ),
    ]
    doc_a = NormalizedDocument(
        id="doc-a",
        title="Document A",
        pages=(NormalizedPage(page_number=1, blocks=tuple(blocks_a)),),
        source="demo",
        checksum="1",
        version="1.0",
        created_at=datetime.now(UTC),
    )

    blocks_b = [
        NormalizedBlock(
            block_id="b1",
            block_type=BlockType.PARAGRAPH,
            text=(
                "This document lacks any headings whatsoever. It is just a very long "
                "sequence of text that goes on for a while."
            ),
            order=0,
        ),
        NormalizedBlock(
            block_id="b2",
            block_type=BlockType.PARAGRAPH,
            text=(
                "Because there are no headings to delineate semantics, the engine "
                "must fall back to fixed-size rules."
            ),
            order=1,
        ),
        NormalizedBlock(
            block_id="b3",
            block_type=BlockType.PARAGRAPH,
            text=(
                "This ensures no downstream context window limits are breached "
                "by a single massive chunk."
            ),
            order=2,
        ),
    ]
    doc_b = NormalizedDocument(
        id="doc-b",
        title="Document B",
        pages=(NormalizedPage(page_number=1, blocks=tuple(blocks_b)),),
        source="demo",
        checksum="2",
        version="1.0",
        created_at=datetime.now(UTC),
    )

    print_results("Document A (Structured)", engine, doc_a)
    print_results("Document B (Unstructured)", engine, doc_b)


if __name__ == "__main__":
    main()
