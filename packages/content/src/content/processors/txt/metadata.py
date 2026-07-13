from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType
from ...normalized.metadata import DocumentMetadata


def extract_metadata(
    blocks: tuple[NormalizedBlock, ...], filename: str
) -> tuple[str, DocumentMetadata]:
    """
    Priority: First Heading -> First Non-Empty Paragraph -> Filename
    """
    title = None

    if not title:
        for block in blocks:
            if block.block_type == BlockType.HEADING and block.text.strip():
                title = block.text.strip()
                break

    if not title:
        for block in blocks:
            if block.block_type == BlockType.PARAGRAPH and block.text.strip():
                title = block.text.strip()
                break

    if not title:
        title = filename

    return title, DocumentMetadata(author=None)
