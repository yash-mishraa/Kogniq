from abc import ABC, abstractmethod
from typing import Any


class AbstractStreamReference(ABC):
    """
    Abstract interface for streaming resource content.
    Future storage providers (Local, S3, MinIO) will implement this.
    Does not implement any reading or IO logic itself.
    """

    @abstractmethod
    def open_stream(self) -> Any:
        """Opens the stream for reading."""
