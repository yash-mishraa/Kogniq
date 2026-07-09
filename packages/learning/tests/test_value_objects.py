import pytest

from learning.domain.value_objects import (
    Difficulty,
    DifficultyLevel,
    ResourceReference,
    ResourceType,
    Tag,
)


def test_difficulty_validation() -> None:
    with pytest.raises(ValueError, match=r"between 0.0 and 100.0"):
        Difficulty(level=DifficultyLevel.BEGINNER, score=-1.0)

    diff = Difficulty(level=DifficultyLevel.BEGINNER, score=50.0)
    assert diff.level == DifficultyLevel.BEGINNER


def test_tag_normalization() -> None:
    tag = Tag(value="  PYTHON  ")
    assert tag.value == "python"

    with pytest.raises(ValueError):
        Tag(value="   ")


def test_resource_reference_validation() -> None:
    with pytest.raises(ValueError):
        ResourceReference(resource_type=ResourceType.VIDEO, uri="  ")
