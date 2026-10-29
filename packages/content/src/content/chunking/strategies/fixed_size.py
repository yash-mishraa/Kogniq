import re
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

    def __init__(self, max_characters: int = 1500, overlap_characters: int = 0) -> None:
        if max_characters <= 0:
            raise ChunkStrategyError(f"max_characters must be > 0, got {max_characters}")
        if overlap_characters < 0:
            raise ChunkStrategyError(
                f"overlap_characters must be >= 0, got {overlap_characters}"
            )
        if overlap_characters >= max_characters:
            raise ChunkStrategyError(
                "overlap_characters must be smaller than max_characters "
                f"({overlap_characters} >= {max_characters})"
            )
        self.max_characters = max_characters
        self.overlap_characters = overlap_characters

    def chunk(self, document: NormalizedDocument) -> ChunkCollection:
        chunks: list[Chunk] = []
        chunk_index = 0

        current_section: str | None = None
        current_page_number: int | None = None
        current_blocks: list[str] = []
        current_char_count = 0
        pending_overlap: list[str] = []
        pending_overlap_page: int | None = None

        def finalize_chunk() -> None:
            nonlocal chunk_index, current_section, current_page_number
            nonlocal current_blocks, current_char_count, pending_overlap, pending_overlap_page

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

            # Preserve an optional trailing overlap for the next chunk. The
            # overlap is measured on the final joined text so the configured
            # budget is meaningful to the caller.
            pending_overlap = []
            pending_overlap_page = current_page_number
            if self.overlap_characters > 0:
                used = 0
                carry: list[str] = []
                for sentence in reversed(current_blocks):
                    added = len(sentence) + (1 if carry else 0)
                    if used + added > self.overlap_characters:
                        break
                    carry.insert(0, sentence)
                    used += added
                pending_overlap = carry

            current_blocks = []
            current_char_count = 0
            current_page_number = None

        def split_sentences(text: str) -> list[str]:
            # Positive lookbehind for punctuation, positive lookahead for space + capital/number
            sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
            return [s.strip() for s in sentences if s.strip()]

        def traverse_blocks(blocks: tuple[NormalizedBlock, ...], page_num: int) -> None:
            nonlocal current_section, current_page_number, current_char_count, current_blocks
            nonlocal pending_overlap
            for block in blocks:
                text = block.text.strip() if block.text else ""
                if not text:
                    continue

                new_section = text if block.block_type == BlockType.HEADING else current_section

                # Split block into sentences to avoid giant chunks
                sentences = split_sentences(text)

                for sentence in sentences:
                    sentence_len = len(sentence)
                    if current_blocks and (
                        current_char_count + 1 + sentence_len > self.max_characters
                    ):
                        finalize_chunk()
                        current_section = new_section
                        if pending_overlap:
                            current_blocks = list(pending_overlap)
                            current_char_count = sum(len(s) for s in current_blocks) + len(
                                current_blocks
                            ) - 1
                            current_page_number = pending_overlap_page
                            pending_overlap = []

                    current_section = new_section
                    current_blocks.append(sentence)
                    current_char_count += sentence_len + (1 if len(current_blocks) > 1 else 0)
                    if current_page_number is None:
                        current_page_number = page_num

                if block.children:
                    traverse_blocks(block.children, page_num)

        for page in document.pages:
            traverse_blocks(page.blocks, page.page_number)

        finalize_chunk()

        return ChunkCollection(chunks=tuple(chunks))
