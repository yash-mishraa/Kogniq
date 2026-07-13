import io
from datetime import UTC, datetime

import pytest

from content.normalized.enums import BlockType
from content.processors.txt import TXTProcessor
from content.processors.txt.exceptions import TXTEmptyError, TXTUnsupportedEncodingError
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

def create_handle(data: bytes, filename: str = "test.txt") -> ResourceHandle:
    return ResourceHandle(
        id="test_id_123",
        filename=filename,
        extension=".txt",
        mime_type="text/plain",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy"),
        size_bytes=len(data),
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(data),
        lifecycle_state=LifecycleState.CREATED,
    )

def test_txt_processor_success() -> None:
    text = (
        "Core Title\n"
        "==========\n"
        "\n"
        "This is paragraph 1.\n"
        "It has two lines.\n"
        "\n"
        "\n" 
        "# Markdown Heading\n"
        "\n"
        "ALL CAPS HEADING\n" 
        "\n"
        "Paragraph 2.\n"
    )
    handle = create_handle(text.encode('utf-8'))
    processor = TXTProcessor()
    doc = processor.process(handle)
    
    assert doc.title == "Core Title"
    blocks = doc.pages[0].blocks
    
    assert blocks[0].block_type == BlockType.HEADING
    assert blocks[0].text == "Core Title"
    
    assert blocks[1].block_type == BlockType.PARAGRAPH
    assert blocks[1].text == "This is paragraph 1.\nIt has two lines."
    
    assert blocks[2].block_type == BlockType.HEADING
    assert blocks[2].text == "# Markdown Heading"
    
    assert blocks[3].block_type == BlockType.HEADING
    assert blocks[3].text == "ALL CAPS HEADING"
    
    assert blocks[4].block_type == BlockType.PARAGRAPH
    assert blocks[4].text == "Paragraph 2."

def test_mixed_line_endings() -> None:
    text = "Heading\r\n=======\rParagraph 1 line 1\nParagraph 1 line 2\r\n\r\nParagraph 2"
    handle = create_handle(text.encode('utf-8'))
    doc = TXTProcessor().process(handle)
    blocks = doc.pages[0].blocks
    
    assert blocks[0].block_type == BlockType.HEADING
    assert blocks[0].text == "Heading"
    assert blocks[1].block_type == BlockType.PARAGRAPH
    assert blocks[1].text == "Paragraph 1 line 1\nParagraph 1 line 2"
    assert blocks[2].block_type == BlockType.PARAGRAPH
    assert blocks[2].text == "Paragraph 2"

def test_heading_priority() -> None:
    text = "# A MARKDOWN HEADING\n"
    handle = create_handle(text.encode('utf-8'))
    doc = TXTProcessor().process(handle)
    assert doc.pages[0].blocks[0].text == "# A MARKDOWN HEADING"

def test_very_long_all_caps() -> None:
    long_caps = "A" * 150
    text = f"{long_caps}\n\nNormal paragraph."
    handle = create_handle(text.encode('utf-8'))
    doc = TXTProcessor().process(handle)
    blocks = doc.pages[0].blocks
    
    assert blocks[0].block_type == BlockType.PARAGRAPH
    assert blocks[0].text == long_caps

def test_whitespace_only() -> None:
    handle = create_handle(b"   \n  \t  \n")
    with pytest.raises(TXTEmptyError):
        TXTProcessor().process(handle)

def test_utf8_bom() -> None:
    text = "BOM Title\n=========\nPara"
    data = b'\xef\xbb\xbf' + text.encode('utf-8')
    handle = create_handle(data)
    doc = TXTProcessor().process(handle)
    assert doc.title == "BOM Title"
    
def test_unsupported_encoding() -> None:
    data = "Hello".encode('utf-16')
    handle = create_handle(data)
    with pytest.raises(TXTUnsupportedEncodingError):
        TXTProcessor().process(handle)

def test_plugin_registration() -> None:
    from content.plugins.registry import ProcessorRegistry
    registry = ProcessorRegistry()
    registry.register(TXTProcessor())
    processor = registry.processor_for_extension("txt")
    assert isinstance(processor, TXTProcessor)
