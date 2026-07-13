from .exceptions import (
    DOCXCorruptedError,
    DOCXEmptyError,
    DOCXProcessorError,
    DOCXUnsupportedError,
)
from .processor import DOCXProcessor

__all__ = [
    "DOCXCorruptedError",
    "DOCXEmptyError",
    "DOCXProcessor",
    "DOCXProcessorError",
    "DOCXUnsupportedError",
]
