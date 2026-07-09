from dataclasses import dataclass

from .block import NormalizedBlock
from .validation import InvalidPageError, validate_positive


@dataclass(frozen=True, kw_only=True)
class NormalizedPage:
    """Represents a single page in a normalized document."""

    page_number: int
    blocks: tuple[NormalizedBlock, ...]
    width: float | None = None
    height: float | None = None
    rotation: int | None = None

    def __post_init__(self) -> None:
        validate_positive(self.page_number, "page_number", InvalidPageError)
