from abc import ABC, abstractmethod

from ..domain.entities import LearningResource
from .processor_info import ProcessorInfo


class AbstractContentProcessor(ABC):
    """Abstract interface for all concrete content processors."""

    @property
    @abstractmethod
    def processor_info(self) -> ProcessorInfo:
        """Returns the metadata and capabilities of the processor."""

    @abstractmethod
    def process(self, resource: LearningResource) -> str:
        """Processes a raw learning resource and returns the parsed text content."""
