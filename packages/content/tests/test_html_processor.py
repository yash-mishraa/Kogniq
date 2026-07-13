import io
from datetime import UTC, datetime

import pytest

from content.normalized.enums import BlockType
from content.plugins.registry import ProcessorRegistry
from content.processors.html import HTMLProcessor
from content.processors.html.exceptions import (
    HTMLEmptyError,
    HTMLUnsupportedEncodingError,
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


def create_handle(data: bytes, filename: str = "test.html") -> ResourceHandle:
    return ResourceHandle(
        id="test_id_html",
        filename=filename,
        extension=".html",
        mime_type="text/html",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy"),
        size_bytes=len(data),
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(data),
        lifecycle_state=LifecycleState.CREATED,
    )


def test_html_processor_success() -> None:
    html = """
    <html>
        <head>
            <title>Test Document</title>
            <meta name="description" content="This is a test document.">
            <meta name="keywords" content="test, html">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph with <b>bold</b> and <i>italic</i> text.</p>
            
            <h2>Nested Heading</h2>
            <ul>
                <li>List item 1</li>
                <li>List item 2 with <a href="#">a link</a></li>
            </ul>
            
            <blockquote>
                A beautiful quote.
            </blockquote>
            
            <pre><code>
            def test():
                pass
            </code></pre>
            
            <table>
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                </tr>
                <tr>
                    <td>Data 1</td>
                    <td>Data 2</td>
                </tr>
            </table>
            
            <!-- Ignored elements -->
            <script>console.log('ignored');</script>
            <nav>Ignored Nav</nav>
            <footer>Ignored Footer</footer>
            
            <div>
                Loose text in div.
                <p>Nested p in div</p>
            </div>
        </body>
    </html>
    """
    handle = create_handle(html.encode("utf-8"))
    processor = HTMLProcessor()
    doc = processor.process(handle)
    
    assert doc.title == "Test Document"
    assert doc.metadata is not None
    assert doc.metadata.subject == "This is a test document."
    assert doc.metadata.keywords == ("test", "html")
    
    blocks = doc.pages[0].blocks
    
    # 1. h1
    assert blocks[0].block_type == BlockType.HEADING
    assert blocks[0].text == "Main Heading"
    
    # 2. p
    assert blocks[1].block_type == BlockType.PARAGRAPH
    assert blocks[1].text == "This is a paragraph with bold and italic text."
    
    # 3. h2
    assert blocks[2].block_type == BlockType.HEADING
    assert blocks[2].text == "Nested Heading"
    
    # 4, 5. li (lists map to LIST directly from 'li')
    assert blocks[3].block_type == BlockType.LIST
    assert blocks[3].text == "List item 1"
    
    assert blocks[4].block_type == BlockType.LIST
    assert blocks[4].text == "List item 2 with a link"
    
    # 6. blockquote
    assert blocks[5].block_type == BlockType.QUOTE
    assert blocks[5].text == "A beautiful quote."
    
    # 7. pre/code
    assert blocks[6].block_type == BlockType.CODE
    assert "def test():" in blocks[6].text
    
    # 8. table
    assert blocks[7].block_type == BlockType.TABLE
    assert "| Header 1 | Header 2 |" in blocks[7].text
    assert "| Data 1 | Data 2 |" in blocks[7].text
    
    # 9. Loose text in div
    assert blocks[8].block_type == BlockType.PARAGRAPH
    assert blocks[8].text == "Loose text in div."
    
    # 10. p in div
    assert blocks[9].block_type == BlockType.PARAGRAPH
    assert blocks[9].text == "Nested p in div"


def test_title_fallback() -> None:
    # 1. No title -> fallback to first h1
    html = "<body><h1>Fallback 1</h1><p>Text</p></body>"
    doc = HTMLProcessor().process(create_handle(html.encode("utf-8")))
    assert doc.title == "Fallback 1"
    
    # 2. No title, no h1 -> fallback to first heading
    html = "<body><h3>Fallback 2</h3><p>Text</p></body>"
    doc = HTMLProcessor().process(create_handle(html.encode("utf-8")))
    assert doc.title == "Fallback 2"
    
    # 3. No title, no headings -> fallback to filename
    html = "<body><p>Text</p></body>"
    doc = HTMLProcessor().process(create_handle(html.encode("utf-8"), "fallback3.html"))
    assert doc.title == "fallback3.html"


def test_empty_html() -> None:
    # Just body with ignored stuff
    html = "<body><script>x = 1</script></body>"
    with pytest.raises(HTMLEmptyError):
        HTMLProcessor().process(create_handle(html.encode("utf-8")))


def test_malformed_html() -> None:
    # No body at all
    html = "Just some text with no tags at all"
    # Actually BS4 will wrap it in body automatically.
    # So we should test a truly malformed one if possible,
    # or just trust BS4 is tolerant and will wrap it. 
    # Let's see if BS4 wraps it in body.
    doc = HTMLProcessor().process(create_handle(html.encode("utf-8")))
    assert doc.pages[0].blocks[0].text == "Just some text with no tags at all"
    
    # What raises HTMLMalformedError? "HTML document has no <body> tag."
    # Can we trick BS4 into not producing a body?
    # Maybe empty string?
    with pytest.raises(HTMLEmptyError):
        HTMLProcessor().process(create_handle(b""))


def test_unsupported_encoding() -> None:
    data = "Hello".encode('utf-16')
    handle = create_handle(data)
    with pytest.raises(HTMLUnsupportedEncodingError):
        HTMLProcessor().process(handle)


def test_registry_integration() -> None:
    registry = ProcessorRegistry()
    registry.register(HTMLProcessor())
    
    assert registry.has_processor("kogniq-html")
    assert registry.is_supported(extension="html")
    assert registry.is_supported(extension="htm")
    assert registry.is_supported(mime_type="text/html")
