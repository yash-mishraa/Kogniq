from dataclasses import dataclass

from .enums import BlockType
from .validation import InvalidBlockError, validate_non_negative


@dataclass(frozen=True, kw_only=True)
class NormalizedBlock:
    """Represents a logical layout block (paragraph, heading, table, etc.)."""

    block_id: str
    block_type: BlockType
    text: str
    bbox: tuple[float, float, float, float] | None = None
    order: int
    children: tuple["NormalizedBlock", ...] | None = None

    def __post_init__(self) -> None:
        validate_non_negative(self.order, "order", InvalidBlockError)
