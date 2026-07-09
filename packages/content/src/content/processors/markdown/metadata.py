from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType
from ...normalized.metadata import DocumentMetadata


def extract_metadata(blocks: tuple[NormalizedBlock, ...]) -> tuple[str | None, DocumentMetadata]:
    """
    Extracts the first heading as the title, if available.
    Returns (title, metadata).
    """
    title = None
    for block in blocks:
        if block.block_type == BlockType.HEADING and block.text.strip():
            title = block.text.strip()
            break
            
    return title, DocumentMetadata()
