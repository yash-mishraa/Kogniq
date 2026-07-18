import pytest

from learning_content.exceptions import InvalidLearningContentError
from learning_content.statistics import LearningContentStatistics


def test_statistics_valid() -> None:
    stats = LearningContentStatistics(
        character_count=100,
        word_count=20,
        estimated_tokens=30,
        processing_time_ms=10.0,
        confidence=0.9,
    )
    assert stats.character_count == 100


def test_statistics_negative_counts() -> None:
    with pytest.raises(InvalidLearningContentError, match="Character count cannot be negative"):
        LearningContentStatistics(
            character_count=-1,
            word_count=20,
            estimated_tokens=30,
            processing_time_ms=10.0,
            confidence=0.9,
        )


def test_statistics_invalid_confidence_high() -> None:
    with pytest.raises(
        InvalidLearningContentError, match=r"Confidence must be between 0\.0 and 1\.0"
    ):
        LearningContentStatistics(
            character_count=100,
            word_count=20,
            estimated_tokens=30,
            processing_time_ms=10.0,
            confidence=1.1,
        )


def test_statistics_invalid_confidence_low() -> None:
    with pytest.raises(
        InvalidLearningContentError, match=r"Confidence must be between 0\.0 and 1\.0"
    ):
        LearningContentStatistics(
            character_count=100,
            word_count=20,
            estimated_tokens=30,
            processing_time_ms=10.0,
            confidence=-0.1,
        )
