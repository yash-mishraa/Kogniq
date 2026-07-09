from dataclasses import FrozenInstanceError

import pytest

from education.domain import (
    ConfidenceScore,
    DifficultyBand,
    DifficultyLevel,
    EducationalMetadata,
    ImportanceScore,
    InvalidConceptError,
)


def test_difficulty_level_valid() -> None:
    dl = DifficultyLevel(band=DifficultyBand.INTERMEDIATE, score=0.5)
    assert dl.band == DifficultyBand.INTERMEDIATE
    assert dl.score == 0.5


def test_difficulty_level_invalid() -> None:
    with pytest.raises(InvalidConceptError, match=r"between 0\.0 and 1\.0"):
        DifficultyLevel(band=DifficultyBand.ADVANCED, score=1.5)
    with pytest.raises(InvalidConceptError, match=r"between 0\.0 and 1\.0"):
        DifficultyLevel(band=DifficultyBand.ADVANCED, score=-0.1)


def test_importance_score_valid() -> None:
    score = ImportanceScore(value=0.9)
    assert score.value == 0.9


def test_importance_score_invalid() -> None:
    with pytest.raises(InvalidConceptError, match=r"between 0\.0 and 1\.0"):
        ImportanceScore(value=1.1)


def test_confidence_score_valid() -> None:
    score = ConfidenceScore(value=0.95)
    assert score.value == 0.95


def test_confidence_score_invalid() -> None:
    with pytest.raises(InvalidConceptError, match=r"between 0\.0 and 1\.0"):
        ConfidenceScore(value=-0.05)


def test_metadata_immutability() -> None:
    meta = EducationalMetadata(attributes={"page": "12"})
    with pytest.raises(FrozenInstanceError):
        meta.attributes = {"page": "13"}  # type: ignore
