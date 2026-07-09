import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

# Ensure local packages are accessible
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.processors.markdown import MarkdownProcessor
from content.resource import (
    AbstractStreamReference,
    Checksum,
    ChecksumAlgorithm,
    ContentSource,
    LifecycleState,
    ResourceHandle,
    ResourceMetadata as HandleMetadata,
)


class LocalFileStreamReference(AbstractStreamReference):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def open_stream(self) -> IO[bytes]:
        return self.file_path.open("rb")


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print("Usage: uv run python dev/demo_markdown_processor.py [path_to_md]")
            print("If no path is provided, it defaults to:")
            print("  dev/sample_documents/sample.md")
            sys.exit(0)
        md_path = Path(sys.argv[1]).resolve()
    else:
        md_path = Path(__file__).parent / "sample_documents" / "sample.md"

    if not md_path.exists():
        print(f"Error: Could not find Markdown file at {md_path}")
        print("Usage: uv run python dev/demo_markdown_processor.py [path_to_md]")
        sys.exit(1)

    stream_ref = LocalFileStreamReference(md_path)

    handle = ResourceHandle(
        id="demo_md_001",
        filename=md_path.name,
        extension=md_path.suffix,
        mime_type="text/markdown",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy_checksum"),
        size_bytes=md_path.stat().st_size,
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=stream_ref,
        lifecycle_state=LifecycleState.CREATED,
    )

    print(f"Processing: {md_path.name}...\n")
    processor = MarkdownProcessor()
    doc = processor.process(handle)

    print("-" * 40)
    print(f"Title       : {doc.title}")
    
    total_blocks = sum(len(page.blocks) for page in doc.pages)
    print(f"Block count : {total_blocks}")
    print(f"Statistics  : {doc.statistics}")
    print("-" * 40)
    print()

    if not doc.pages or not doc.pages[0].blocks:
        print("No blocks found.")
        return

    first_page = doc.pages[0]
    print("\nFirst 5 blocks text:")
    
    for i, block in enumerate(first_page.blocks[:5], start=1):
        text = block.text.replace('\n', ' ')
        if len(text) > 100:
            text = text[:97] + "..."
        print(f"  [{i}] ({block.block_type.name}) {text}")

if __name__ == "__main__":
    main()
