import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

# Ensure the local packages are accessible
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.processors.pdf import PDFProcessor
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
    """Local file implementation of AbstractStreamReference for developer verification."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def open_stream(self) -> IO[bytes]:
        return self.file_path.open("rb")


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print("Usage: uv run python dev/demo_pdf_processor.py [path_to_pdf]")
            print("If no path is provided, it defaults to:")
            print("  dev/sample_documents/transformer_paper.pdf")
            sys.exit(0)
        pdf_path = Path(sys.argv[1]).resolve()
    else:
        pdf_path = Path(__file__).parent / "sample_documents" / "transformer_paper.pdf"

    if not pdf_path.exists():
        print(f"Error: Could not find PDF at {pdf_path}")
        print("Please ensure the document exists before running this script.")
        print("Usage: uv run python dev/demo_pdf_processor.py [path_to_pdf]")
        sys.exit(1)

    # 1. Create concrete StreamReference
    stream_ref = LocalFileStreamReference(pdf_path)

    # 2. Construct valid ResourceHandle
    handle = ResourceHandle(
        id="demo_pdf_001",
        filename=pdf_path.name,
        extension=pdf_path.suffix,
        mime_type="application/pdf",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy_checksum_for_demo"),
        size_bytes=pdf_path.stat().st_size,
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=stream_ref,
        lifecycle_state=LifecycleState.CREATED,
    )

    # 3. Instantiate Processor & Process
    print(f"Processing: {pdf_path.name}...\n")
    processor = PDFProcessor()
    doc = processor.process(handle)

    # 4. Print Document Level Info
    print("-" * 40)
    print(f"Title       : {doc.title}")
    author_str = doc.metadata.author if doc.metadata and doc.metadata.author else "Unknown"
    print(f"Author      : {author_str}")
    print(f"Page count  : {len(doc.pages)}")
    total_blocks = sum(len(page.blocks) for page in doc.pages)
    print(f"Total blocks: {total_blocks}")
    print(f"Metadata    : {doc.metadata}")
    print(f"Statistics  : {doc.statistics}")
    print("-" * 40)
    print()

    # 5. Print First Page Info
    if not doc.pages:
        print("No pages found.")
        return

    first_page = doc.pages[0]
    print(f"First page number : {first_page.page_number}")
    print(f"Number of blocks  : {len(first_page.blocks)}")
    print("\nFirst 5 blocks text:")

    for i, block in enumerate(first_page.blocks[:5], start=1):
        # Truncate text for cleaner printing if it's too long
        text = block.text.replace("\n", " ")
        if len(text) > 100:
            text = text[:97] + "..."
        print(f"  [{i}] {text}")


if __name__ == "__main__":
    main()
