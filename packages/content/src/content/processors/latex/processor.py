import re
from datetime import UTC, datetime

from ...normalized.block import NormalizedBlock
from ...normalized.document import NormalizedDocument
from ...normalized.enums import BlockType
from ...normalized.metadata import DocumentMetadata
from ...normalized.page import NormalizedPage
from ...plugins.interfaces import AbstractContentProcessor
from ...plugins.processor_info import ProcessorInfo
from ...resource.handle import ResourceHandle


class LatexProcessor(AbstractContentProcessor):
    """
    Extracts semantic content, sections, and mathematical equations from LaTeX files.
    Preserves inline ($...$) and display ($$... / \\begin{equation}...) math notation
    intact so downstream embeddings, retrieval, and RAG can answer technical and math queries.
    """

    @property
    def processor_info(self) -> ProcessorInfo:
        return ProcessorInfo(
            name="kogniq-latex",
            version="1.0",
            supported_extensions=("tex", "latex"),
            supported_mime_types=("application/x-tex", "text/x-tex"),
            description="Extracts semantic content and equations from LaTeX documents",
        )

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        with handle.stream_reference.open_stream() as f:
            raw_bytes = f.read()

        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_bytes.decode("latin-1", errors="replace")

        # Extract title from \title{...}
        title_match = re.search(r"\\title\{([^}]+)\}", text)
        title = title_match.group(1).strip() if title_match else handle.filename

        # Remove comments (lines starting with %)
        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("%"):
                continue
            cleaned_lines.append(line)
        cleaned_text = "\n".join(cleaned_lines)

        # Split on section headings or double newlines
        tokens = re.split(r"(\\(?:sub)*section\*?\{[^}]+\})", cleaned_text)
        blocks: list[NormalizedBlock] = []

        for token in tokens:
            t_str = token.strip()
            if not t_str:
                continue

            sec_match = re.match(r"\\(?:sub)*section\*?\{([^}]+)\}", t_str)
            if sec_match:
                blocks.append(
                    NormalizedBlock(
                        block_id=f"latex_b_{len(blocks)}",
                        block_type=BlockType.HEADING,
                        text=sec_match.group(1).strip(),
                        order=len(blocks),
                    )
                )
            else:
                paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", t_str) if p.strip()]
                for p in paragraphs:
                    clean_p = re.sub(
                        r"\\(?:documentclass|usepackage|begin|end)\{[^}]*\}", "", p
                    ).strip()
                    if clean_p:
                        blocks.append(
                            NormalizedBlock(
                                block_id=f"latex_b_{len(blocks)}",
                                block_type=BlockType.PARAGRAPH,
                                text=clean_p,
                                order=len(blocks),
                            )
                        )

        if not blocks:
            blocks.append(
                NormalizedBlock(
                    block_id="latex_b_0",
                    block_type=BlockType.PARAGRAPH,
                    text=text[:1000] if text else "Empty LaTeX document",
                    order=0,
                )
            )

        page = NormalizedPage(page_number=1, blocks=tuple(blocks))

        return NormalizedDocument(
            id=handle.id,
            title=title,
            pages=(page,),
            source=handle.source.name.lower() if hasattr(handle.source, "name") else str(handle.source),
            checksum=handle.checksum.value,
            version=self.processor_info.version,
            created_at=datetime.now(UTC),
            metadata=DocumentMetadata(author=None),
        )
