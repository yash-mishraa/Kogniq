"""Generic logger provider contract."""

from logging import Logger
from typing import Protocol


class LoggerProvider(Protocol):
    """Resolve standard-library loggers without exposing backend details."""

    def get_logger(self, name: str) -> Logger:
        """Return a logger for the requested component name."""
        ...
