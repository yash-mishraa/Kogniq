import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.processors.txt import TXTProcessor
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

def create_sample_txt(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "SAMPLE TEXT DOCUMENT\n"
        "====================\n"
        "\n"
        "This is the first paragraph.\n"
        "It spans multiple lines to demonstrate paragraph grouping.\n"
        "\n"
        "# Markdown Subheading\n"
        "\n"
        "Another paragraph after the subheading.\n"
        "\n"
        "ALL CAPS HEADING\n"
        "\n"
        "Final paragraph of the demo.\n"
    )
    path.write_bytes(content.encode("utf-8"))

def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print("Usage: uv run python dev/demo_txt_processor.py [path_to_txt]")
            print("If no path is provided, it defaults to:")
            print("  dev/sample_documents/sample.txt (generated on the fly if missing)")
            sys.exit(0)
        txt_path = Path(sys.argv[1]).resolve()
    else:
        txt_path = Path(__file__).parent / "sample_documents" / "sample.txt"

    if not txt_path.exists():
        if txt_path.name == "sample.txt":
            print("Generating sample.txt...")
            create_sample_txt(txt_path)
        else:
            print(f"Error: Could not find TXT file at {txt_path}")
            sys.exit(1)

    stream_ref = LocalFileStreamReference(txt_path)

    handle = ResourceHandle(
        id="demo_txt_001",
        filename=txt_path.name,
        extension=txt_path.suffix,
        mime_type="text/plain",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy_checksum"),
        size_bytes=txt_path.stat().st_size,
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=stream_ref,
        lifecycle_state=LifecycleState.CREATED,
    )

    print(f"Processing: {txt_path.name}...\n")
    processor = TXTProcessor()
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
