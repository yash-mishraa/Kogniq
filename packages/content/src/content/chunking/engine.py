from ..normalized.block import NormalizedBlock
from ..normalized.document import NormalizedDocument
from ..normalized.enums import BlockType
from .collection import ChunkCollection
from .strategies.base import AbstractChunkStrategy
from .strategies.fixed_size import FixedSizeChunkStrategy
from .strategies.structural import StructuralChunkStrategy


class HybridChunkEngine:
    """Orchestrates chunking strategies based on document structure."""

    def __init__(
        self,
        structural_strategy: AbstractChunkStrategy | None = None,
        fixed_strategy: AbstractChunkStrategy | None = None,
    ) -> None:
        self.structural_strategy = structural_strategy or StructuralChunkStrategy()
        self.fixed_strategy = fixed_strategy or FixedSizeChunkStrategy()

        self._last_selected_strategy: str | None = None

    @property
    def last_selected_strategy(self) -> str | None:
        """Returns the class name of the strategy used for the most recent chunk operation."""
        return self._last_selected_strategy

    def _has_headings(self, document: NormalizedDocument) -> bool:
        """Short-circuiting scan to detect if any block (or child block) is a HEADING."""

        def check_blocks(blocks: tuple[NormalizedBlock, ...]) -> bool:
            for block in blocks:
                if block.block_type == BlockType.HEADING:
                    return True
                if block.children and check_blocks(block.children):
                    return True
            return False

        return any(check_blocks(page.blocks) for page in document.pages)

    def chunk(self, document: NormalizedDocument) -> ChunkCollection:
        """Selects a strategy and delegates chunking to it."""
        strategy = self.structural_strategy if self._has_headings(document) else self.fixed_strategy

        self._last_selected_strategy = strategy.__class__.__name__
        return strategy.chunk(document)
