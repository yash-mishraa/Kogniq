from datetime import UTC, datetime

from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


def _create_content(id_val: str, chars: int, words: int, tokens: int) -> LearningContent:
    return LearningContent(
        id=id_val,
        source_document_id="doc-1",
        source_chunk_ids=("chunk-1",),
        content_type=ContentType.SUMMARY,
        title=f"Title {id_val}",
        body="Body",
        metadata=LearningContentMetadata(
            provider="test",
            model="test",
            model_version="1",
            generation_version="1",
            language="en",
            educational_level="beginner",
            subject="computer_science",
            syllabus="standard",
            prompt_version="1.0",
            tags=("test",),
        ),
        statistics=LearningContentStatistics(
            character_count=chars,
            word_count=words,
            estimated_tokens=tokens,
            processing_time_ms=10.0,
            confidence=0.9,
        ),
        created_at=datetime.now(UTC),
    )


def test_learning_content_collection() -> None:
    c1 = _create_content("1", 10, 2, 3)
    c2 = _create_content("2", 20, 4, 5)

    collection = LearningContentCollection(contents=(c1, c2))

    assert collection.total_items == 2
    assert collection.total_characters == 30
    assert collection.total_words == 6
    assert collection.total_estimated_tokens == 8
