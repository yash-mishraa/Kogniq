import io
from datetime import UTC, datetime

import pytest

from content.normalized import BlockType
from content.processors.markdown import (
    MarkdownEmptyError,
    MarkdownEncodingError,
    MarkdownProcessor,
)
from content.resource import (
    AbstractStreamReference,
    Checksum,
    ChecksumAlgorithm,
    ContentSource,
    LifecycleState,
    ResourceHandle,
    ResourceMetadata as HandleMetadata,
)


class MemoryStreamReference(AbstractStreamReference):
    def __init__(self, data: bytes) -> None:
        self.data = data

    def open_stream(self) -> io.BytesIO:
        return io.BytesIO(self.data)


def create_handle(data: bytes, filename: str = "test.md") -> ResourceHandle:
    return ResourceHandle(
        id="res_md_1",
        filename=filename,
        extension=".md",
        mime_type="text/markdown",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="hash"),
        size_bytes=len(data),
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(data),
        lifecycle_state=LifecycleState.CREATED,
    )


def test_markdown_processor_headings() -> None:
    md = "# Title 1\n## Subtitle 2\n"
    handle = create_handle(md.encode("utf-8"))
    processor = MarkdownProcessor()
    result = processor.process(handle)
    
    assert result.title == "Title 1"
    assert len(result.pages) == 1
    blocks = result.pages[0].blocks
    assert len(blocks) == 2
    assert blocks[0].block_type == BlockType.HEADING
    assert blocks[0].text == "Title 1"
    assert blocks[1].block_type == BlockType.HEADING
    assert blocks[1].text == "Subtitle 2"
    
    stats = result.statistics
    assert stats is not None
    assert stats["headings_extracted"] == 2


def test_markdown_processor_paragraphs() -> None:
    md = "Paragraph 1\n\nParagraph 2\n"
    handle = create_handle(md.encode("utf-8"))
    processor = MarkdownProcessor()
    result = processor.process(handle)
    
    # Title fallback to filename because no headings exist
    assert result.title == "test.md"
    blocks = result.pages[0].blocks
    assert len(blocks) == 2
    assert blocks[0].block_type == BlockType.PARAGRAPH
    assert blocks[0].text == "Paragraph 1"
    assert blocks[1].block_type == BlockType.PARAGRAPH
    assert blocks[1].text == "Paragraph 2"


def test_markdown_processor_lists() -> None:
    md = "* Item 1\n* Item 2\n\n1. First\n2. Second"
    handle = create_handle(md.encode("utf-8"))
    processor = MarkdownProcessor()
    result = processor.process(handle)
    
    blocks = result.pages[0].blocks
    assert len(blocks) == 2
    assert blocks[0].block_type == BlockType.LIST
    assert "- Item 1\n- Item 2" in blocks[0].text
    
    assert blocks[1].block_type == BlockType.LIST
    assert "1. First\n2. Second" in blocks[1].text


def test_markdown_processor_fenced_code() -> None:
    md = "```python\nprint('hello')\n```"
    handle = create_handle(md.encode("utf-8"))
    processor = MarkdownProcessor()
    result = processor.process(handle)
    
    blocks = result.pages[0].blocks
    assert len(blocks) == 1
    assert blocks[0].block_type == BlockType.CODE
    assert "```python\nprint('hello')\n```" in blocks[0].text


def test_markdown_processor_tables() -> None:
    md = "| Header 1 | Header 2 |\n|---|---|\n| Cell 1 | Cell 2 |"
    handle = create_handle(md.encode("utf-8"))
    processor = MarkdownProcessor()
    result = processor.process(handle)
    
    blocks = result.pages[0].blocks
    assert len(blocks) == 1
    assert blocks[0].block_type == BlockType.TABLE
    assert "| Header 1 | Header 2 | \n| Cell 1 | Cell 2 |" in blocks[0].text


def test_markdown_processor_empty() -> None:
    handle = create_handle(b"")
    processor = MarkdownProcessor()
    with pytest.raises(MarkdownEmptyError, match="Markdown file is empty"):
        processor.process(handle)


def test_markdown_processor_invalid_encoding() -> None:
    handle = create_handle(b"\x80\x81\x82")  # Invalid UTF-8
    processor = MarkdownProcessor()
    with pytest.raises(MarkdownEncodingError, match="Failed to decode Markdown file"):
        processor.process(handle)
        

def test_markdown_processor_info() -> None:
    processor = MarkdownProcessor()
    assert processor.processor_info.name == "kogniq-markdown"
    assert "md" in processor.processor_info.supported_extensions
    assert "text/markdown" in processor.processor_info.supported_mime_types
