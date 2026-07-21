import dataclasses

import pytest
from embedding.exceptions import InvalidVectorDimensionError
from embedding.vector import EmbeddingVector


def test_vector_creation() -> None:
    vec = EmbeddingVector(values=(0.1, -0.5, 0.9), dimension=3)
    assert vec.dimension == 3
    assert len(vec.values) == 3
    assert vec.values == (0.1, -0.5, 0.9)


def test_vector_immutability() -> None:
    vec = EmbeddingVector(values=(1.0,), dimension=1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        vec.dimension = 2  # type: ignore[misc]


def test_vector_empty_values_invalid_dimension() -> None:
    with pytest.raises(InvalidVectorDimensionError, match="must exactly match dimension"):
        EmbeddingVector(values=(), dimension=1)


def test_vector_zero_dimension() -> None:
    with pytest.raises(InvalidVectorDimensionError, match="must be > 0"):
        EmbeddingVector(values=(), dimension=0)


def test_vector_negative_dimension() -> None:
    with pytest.raises(InvalidVectorDimensionError, match="must be > 0"):
        EmbeddingVector(values=(-1.0,), dimension=-1)


def test_vector_mismatched_dimension() -> None:
    with pytest.raises(InvalidVectorDimensionError, match="must exactly match dimension"):
        EmbeddingVector(values=(1.0, 2.0), dimension=3)
