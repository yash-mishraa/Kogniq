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
from .exceptions import ChunkStrategyError


class FixedSizeChunkStrategy(AbstractChunkStrategy):
    """Splits documents into fixed-size chunks while preserving block reading order."""

    def __init__(self, max_characters: int = 1500) -> None:
        if max_characters <= 0:
            raise ChunkStrategyError(f"max_characters must be > 0, got {max_characters}")
        self.max_characters = max_characters

    def chunk(self, document: NormalizedDocument) -> ChunkCollection:
        chunks: list[Chunk] = []
        chunk_index = 0

        current_section: str | None = None
        current_page_number: int | None = None
        current_blocks: list[str] = []
        current_char_count = 0

        def finalize_chunk() -> None:
            nonlocal chunk_index, current_section, current_page_number
            nonlocal current_blocks, current_char_count

            if not current_blocks:
                return

            text = "\n".join(current_blocks)

            title = current_section if current_section else f"Chunk {chunk_index}"

            char_count = len(text)
            word_count = len(text.split())
            line_count = len(text.splitlines())
            estimated_tokens = char_count // 4

            metadata = ChunkMetadata(
                processor="fixed-size-chunker",
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
                confidence=1.0,
            )

            new_chunk = Chunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                chunk_index=chunk_index,
                text=text,
                title=title,
                section_title=current_section,
                page_number=current_page_number,
                metadata=metadata,
                statistics=statistics,
                created_at=datetime.now(UTC),
            )
            chunks.append(new_chunk)
            chunk_index += 1

            current_blocks = []
            current_char_count = 0
            current_page_number = None

        def traverse_blocks(blocks: tuple[NormalizedBlock, ...], page_num: int) -> None:
            nonlocal current_section, current_page_number, current_char_count
            for block in blocks:
                text = block.text.strip() if block.text else ""
                if not text:
                    continue

                new_section = text if block.block_type == BlockType.HEADING else current_section

                block_len = len(text)

                # Check if appending this block exceeds the max_characters
                # (account for newline if there are already blocks in buffer)
                additional_len = block_len if not current_blocks else block_len + 1

                if current_blocks and (current_char_count + additional_len > self.max_characters):
                    finalize_chunk()
                    # Re-initialize for new chunk
                    current_section = new_section
                    current_blocks.append(text)
                    current_char_count = block_len
                    current_page_number = page_num
                else:
                    current_section = new_section
                    current_blocks.append(text)
                    current_char_count += additional_len
                    if current_page_number is None:
                        current_page_number = page_num

                if block.children:
                    traverse_blocks(block.children, page_num)

        for page in document.pages:
            traverse_blocks(page.blocks, page.page_number)

        finalize_chunk()

        return ChunkCollection(chunks=tuple(chunks))
