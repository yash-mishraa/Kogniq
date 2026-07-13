import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.processors.html import HTMLProcessor
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

def create_sample_html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample HTML Document</title>
    <meta name="description" content="A robust sample for testing HTML extraction.">
</head>
<body>
    <nav>
        <ul><li><a href="#">Home</a></li></ul>
    </nav>

    <main>
        <h1>Main Educational Content</h1>
        <p>
            This is the first paragraph of the <strong>educational</strong> text.
            It contains inline elements.
        </p>

        <h2>Subtopic Details</h2>
        <ul>
            <li>First important point</li>
            <li>Second important point</li>
        </ul>

        <blockquote>
            Learning is not a spectator sport.
        </blockquote>

        <pre><code>
def learn():
    print("Success")
        </code></pre>

        <table>
            <thead>
                <tr><th>Concept</th><th>Definition</th></tr>
            </thead>
            <tbody>
                <tr><td>HTML</td><td>HyperText Markup Language</td></tr>
            </tbody>
        </table>
    </main>

    <footer>
        <p>Copyright 2026. This should be ignored.</p>
    </footer>
    
    <script>
        console.log("This should also be ignored.");
    </script>
</body>
</html>
"""
    path.write_bytes(content.encode("utf-8"))

def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print("Usage: uv run python dev/demo_html_processor.py [path_to_html]")
            print("If no path is provided, it defaults to:")
            print("  dev/sample_documents/sample.html (generated on the fly if missing)")
            sys.exit(0)
        html_path = Path(sys.argv[1]).resolve()
    else:
        html_path = Path(__file__).parent / "sample_documents" / "sample.html"

    if not html_path.exists():
        if html_path.name == "sample.html":
            print("Generating sample.html...")
            create_sample_html(html_path)
        else:
            print(f"Error: Could not find HTML file at {html_path}")
            sys.exit(1)

    stream_ref = LocalFileStreamReference(html_path)

    handle = ResourceHandle(
        id="demo_html_001",
        filename=html_path.name,
        extension=html_path.suffix,
        mime_type="text/html",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy_checksum"),
        size_bytes=html_path.stat().st_size,
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=stream_ref,
        lifecycle_state=LifecycleState.CREATED,
    )

    print(f"Processing: {html_path.name}...\n")
    processor = HTMLProcessor()
    doc = processor.process(handle)

    print("-" * 40)
    print(f"Processor   : {doc.version}")
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
