from enum import Enum, auto


class BlockType(Enum):
    """Types of logical layout blocks within a normalized document."""

    HEADING = auto()
    PARAGRAPH = auto()
    LIST = auto()
    TABLE = auto()
    IMAGE = auto()
    FORMULA = auto()
    CODE = auto()
    QUOTE = auto()
    UNKNOWN = auto()
