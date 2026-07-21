from dataclasses import dataclass

from .exceptions import InvalidVectorDimensionError


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    """Canonical representation of an embedding vector."""

    values: tuple[float, ...]
    dimension: int

    def __post_init__(self) -> None:
        if self.dimension <= 0:
            raise InvalidVectorDimensionError(f"Dimension must be > 0, got {self.dimension}")
        if len(self.values) != self.dimension:
            raise InvalidVectorDimensionError(
                f"Vector values length ({len(self.values)}) must exactly match "
                f"dimension ({self.dimension})"
            )
