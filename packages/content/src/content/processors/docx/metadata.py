from typing import Any

from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType
from ...normalized.metadata import DocumentMetadata


def extract_metadata(
    doc: Any, blocks: tuple[NormalizedBlock, ...], filename: str
) -> tuple[str, DocumentMetadata]:
    """
    Priority: Core Title -> First Heading -> First Non-Empty Paragraph -> Filename
    """
    title = None
    author = None
    
    if hasattr(doc, "core_properties") and doc.core_properties:
        if getattr(doc.core_properties, "title", None):
            title = str(doc.core_properties.title).strip()
        if getattr(doc.core_properties, "author", None):
            author = str(doc.core_properties.author).strip()
            
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

    return title, DocumentMetadata(author=author if author else None)
