"""Generic exception hierarchy shared across Kogniq packages."""

from shared.exceptions.base import (
    InvalidConfigurationError,
    KogniqError,
    UnsupportedOperationError,
)

__all__ = [
    "InvalidConfigurationError",
    "KogniqError",
    "UnsupportedOperationError",
]
