import io
from datetime import UTC, datetime

from content.normalized.enums import BlockType
from content.processors.latex import LatexProcessor
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


def create_handle(data: bytes, filename: str = "paper.tex") -> ResourceHandle:
    return ResourceHandle(
        id="test_latex_123",
        filename=filename,
        extension=".tex",
        mime_type="application/x-tex",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy_checksum"),
        size_bytes=len(data),
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(data),
        lifecycle_state=LifecycleState.CREATED,
    )


def test_latex_processor_parses_math_and_sections() -> None:
    latex_content = (
        r"\documentclass{article}" "\n"
        r"\title{Quantum Mechanics and Thermodynamics}" "\n"
        r"\begin{document}" "\n"
        r"% This is a comment that should be ignored" "\n"
        r"\section{Energy Mass Equivalence}" "\n"
        r"Einstein's famous formula is given by:" "\n"
        r"\begin{equation}" "\n"
        r"E = mc^2" "\n"
        r"\end{equation}" "\n"
        r"\section{Calculus of Variations}" "\n"
        r"The Euler-Lagrange equation satisfies $\frac{d}{dt}\frac{\partial L}{\partial \dot{q}} = \frac{\partial L}{\partial q}$." "\n"
        r"\end{document}"
    )

    handle = create_handle(latex_content.encode("utf-8"))
    processor = LatexProcessor()
    doc = processor.process(handle)

    assert doc.title == "Quantum Mechanics and Thermodynamics"
    assert len(doc.pages) == 1
    blocks = doc.pages[0].blocks
    assert len(blocks) >= 3

    headings = [b.text for b in blocks if b.block_type == BlockType.HEADING]
    assert "Energy Mass Equivalence" in headings
    assert "Calculus of Variations" in headings

    paragraphs = [b.text for b in blocks if b.block_type == BlockType.PARAGRAPH]
    assert any("E = mc^2" in p for p in paragraphs)
    assert any(r"\frac{d}{dt}" in p for p in paragraphs)
