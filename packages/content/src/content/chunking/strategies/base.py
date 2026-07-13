import abc

from ...normalized.document import NormalizedDocument
from ..collection import ChunkCollection


class AbstractChunkStrategy(abc.ABC):
    """Abstract interface for all chunking strategies."""
    
    @abc.abstractmethod
    def chunk(self, document: NormalizedDocument) -> ChunkCollection:
        """Process a NormalizedDocument into a ChunkCollection."""
