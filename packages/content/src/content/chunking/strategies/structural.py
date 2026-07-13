import uuid
from datetime import UTC, datetime

from ...normalized.block import NormalizedBlock
from ...normalized.document import NormalizedDocument
from ...normalized.enums import BlockType
from ..chunk import Chunk
from ..collection import ChunkCollection
from ..metadata import ChunkMetadata
from ..statistics import ChunkStatistics
from .base import AbstractChunkStrategy


class StructuralChunkStrategy(AbstractChunkStrategy):
    """Chunks documents based strictly on heading structures."""

    def chunk(self, document: NormalizedDocument) -> ChunkCollection:
        chunks: list[Chunk] = []
        chunk_index = 0
        
        current_title = "Introduction"
        current_section = "Introduction"
        current_page_number: int | None = None
        current_blocks: list[str] = []
        
        def finalize_chunk() -> None:
            nonlocal chunk_index, current_title, current_section
            nonlocal current_page_number, current_blocks
            
            if current_blocks:
                text = "\n".join(current_blocks)
                
                # Deterministic approximations
                char_count = len(text)
                word_count = len(text.split())
                line_count = len(text.splitlines())
                # Very rough token estimate (1 token ~ 4 chars for English)
                estimated_tokens = char_count // 4
                
                metadata = ChunkMetadata(
                    processor="structural-chunker",
                    document_version=document.version,
                    source=document.source,
                    checksum=document.checksum,
                    language=document.language,
                    estimated_characters=char_count,
                    estimated_tokens=estimated_tokens,
                )
                
                statistics = ChunkStatistics(
                    character_count=char_count,
                    line_count=line_count,
                    word_count=word_count,
                    estimated_tokens=estimated_tokens,
                    processing_timestamp=datetime.now(UTC),
                    confidence=1.0
                )
                
                new_chunk = Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    chunk_index=chunk_index,
                    text=text,
                    title=current_title,
                    section_title=current_section,
                    page_number=current_page_number,
                    metadata=metadata,
                    statistics=statistics,
                    created_at=datetime.now(UTC)
                )
                chunks.append(new_chunk)
                chunk_index += 1
                
            current_blocks = []
            current_page_number = None

        def traverse_blocks(blocks: tuple[NormalizedBlock, ...], page_num: int) -> None:
            nonlocal current_title, current_section, current_page_number
            for block in blocks:
                text = block.text.strip() if block.text else ""
                if not text:
                    continue
                    
                if block.block_type == BlockType.HEADING:
                    finalize_chunk()
                    current_title = text
                    current_section = text
                    current_blocks.append(text)
                    if current_page_number is None:
                        current_page_number = page_num
                else:
                    current_blocks.append(text)
                    if current_page_number is None:
                        current_page_number = page_num
                        
                if block.children:
                    traverse_blocks(block.children, page_num)

        for page in document.pages:
            traverse_blocks(page.blocks, page.page_number)
            
        finalize_chunk()
        
        return ChunkCollection(chunks=tuple(chunks))
