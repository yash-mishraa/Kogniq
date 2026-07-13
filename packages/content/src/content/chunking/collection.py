from dataclasses import dataclass

from .chunk import Chunk


@dataclass(frozen=True, kw_only=True)
class ChunkCollection:
    """An immutable collection of Chunks preserving insertion order."""
    chunks: tuple[Chunk, ...]
    
    @property
    def total_chunks(self) -> int:
        return len(self.chunks)
        
    @property
    def total_characters(self) -> int:
        return sum(c.statistics.character_count for c in self.chunks)
        
    @property
    def total_words(self) -> int:
        return sum(c.statistics.word_count for c in self.chunks)
        
    @property
    def total_estimated_tokens(self) -> int:
        return sum(c.statistics.estimated_tokens for c in self.chunks)
