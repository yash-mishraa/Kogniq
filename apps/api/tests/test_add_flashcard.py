from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.learning.add_flashcard import AddFlashcardRequest, AddFlashcardUseCase


@pytest.mark.asyncio
async def test_add_flashcard_success() -> None:
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = MagicMock(user_id="user-123")
    
    authorization_service = AsyncMock()
    
    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value.__enter__.return_value = uow
    
    doc = MagicMock(user_id="user-123")
    uow.documents.get = AsyncMock(return_value=doc)
    
    from learning_content.content import LearningContent
    from learning_content.entities import FlashcardCollection
    from learning_content.enums import ContentType
    from learning_content.metadata import LearningContentMetadata
    from learning_content.statistics import LearningContentStatistics
    
    empty_collection = FlashcardCollection(flashcards=tuple())
    content = LearningContent(
        id="lc-1", source_document_id="doc-123", source_chunk_ids=("c1",),
        content_type=ContentType.FLASHCARDS, title="Flashcards", body=empty_collection.to_json(),
        metadata=LearningContentMetadata(
            provider="test", model="test", model_version="1", generation_version="1",
            language="en", educational_level="college", subject="cs", syllabus="none",
            prompt_version="1", tags=tuple()
        ),
        statistics=LearningContentStatistics(character_count=0, word_count=0, estimated_tokens=0, processing_time_ms=0.0, confidence=1.0),
        created_at=datetime.now(UTC)
    )
    uow.learning.list_by_document = AsyncMock(return_value=[content])
    uow.learning.save = AsyncMock()
    
    use_case = AddFlashcardUseCase(auth_service, authorization_service, uow_factory)
    
    req = AddFlashcardRequest(
        document_id="doc-123", token="valid_token", question="Q1", answer="A1", difficulty="easy", idempotency_key="ik1"
    )
    
    res = await use_case.execute(req)
    assert res.status == "success"
    
    uow.learning.save.assert_called_once()
    saved_content = uow.learning.save.call_args[0][0]
    import json
    saved_body = json.loads(saved_content.body)
    assert len(saved_body) == 1
    assert saved_body[0]["question"] == "Q1"
    assert "idempotency:ik1" in saved_content.metadata.tags

    # test idempotency duplicate
    content_idempotent = LearningContent(
        id="lc-1", source_document_id="doc-123", source_chunk_ids=("c1",),
        content_type=ContentType.FLASHCARDS, title="Flashcards", body=empty_collection.to_json(),
        metadata=LearningContentMetadata(
            provider="test", model="test", model_version="1", generation_version="1",
            language="en", educational_level="college", subject="cs", syllabus="none",
            prompt_version="1", tags=("idempotency:ik1",)
        ),
        statistics=LearningContentStatistics(character_count=0, word_count=0, estimated_tokens=0, processing_time_ms=0.0, confidence=1.0),
        created_at=datetime.now(UTC)
    )
    uow.learning.list_by_document = AsyncMock(return_value=[content_idempotent])
    res_dup = await use_case.execute(req)
    assert res_dup.status == "duplicate"





