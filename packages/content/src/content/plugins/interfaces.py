from abc import ABC, abstractmethod

from ..normalized.document import NormalizedDocument
from ..resource.handle import ResourceHandle
from .processor_info import ProcessorInfo


class AbstractContentProcessor(ABC):
    """Abstract interface for all concrete content processors."""

    @property
    @abstractmethod
    def processor_info(self) -> ProcessorInfo:
        """Returns the metadata and capabilities of the processor."""

    @abstractmethod
    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        """Processes a raw resource handle and returns a normalized document."""
