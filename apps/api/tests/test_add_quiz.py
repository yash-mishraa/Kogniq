from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.learning.add_quiz import AddQuizQuestionRequest, AddQuizQuestionUseCase


@pytest.mark.asyncio
async def test_add_quiz_success() -> None:
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = MagicMock(user_id="user-123")
    
    authorization_service = AsyncMock()
    
    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value.__enter__.return_value = uow
    
    doc = MagicMock(user_id="user-123")
    uow.documents.get = AsyncMock(return_value=doc)
    
    from learning_content.content import LearningContent
    from learning_content.entities import QuizCollection
    from learning_content.enums import ContentType
    from learning_content.metadata import LearningContentMetadata
    from learning_content.statistics import LearningContentStatistics
    
    empty_collection = QuizCollection(questions=tuple())
    content = LearningContent(
        id="lc-1", source_document_id="doc-123", source_chunk_ids=("c1",),
        content_type=ContentType.QUIZ, title="Quiz", body=empty_collection.to_json(),
        metadata=LearningContentMetadata(
            provider="test", model="test", model_version="1", generation_version="1",
            language="en", educational_level="college", subject="cs", syllabus="none",
            prompt_version="1", tags=tuple(), generation_id="1"
        ),
        statistics=LearningContentStatistics(character_count=0, word_count=0, estimated_tokens=0, processing_time_ms=0.0, confidence=1.0),
        created_at=datetime.now(UTC)
    )
    uow.learning.list_by_document = AsyncMock(return_value=[content])
    uow.learning.save = AsyncMock()
    
    use_case = AddQuizQuestionUseCase(auth_service, authorization_service, uow_factory)
    
    req = AddQuizQuestionRequest(
        document_id="doc-123", token="valid_token", question="Q1",
        options=["O1", "O2", "O3", "O4"], correct_answer="O1", explanation="E1",
        difficulty="easy", idempotency_key="ik1"
    )
    
    res = await use_case.execute(req)
    assert res.status == "success"
    
    uow.learning.save.assert_called_once()
    saved_content = uow.learning.save.call_args[0][0]
    import json
    saved_body = json.loads(saved_content.body)
    assert len(saved_body) == 1
    assert saved_body[0]["question"] == "Q1"
    assert saved_body[0]["options"][0]["text"] == "O1"
    assert "idempotency:ik1" in saved_content.metadata.tags

    # test idempotency duplicate
    content_idempotent = LearningContent(
        id="lc-1", source_document_id="doc-123", source_chunk_ids=("c1",),
        content_type=ContentType.QUIZ, title="Quiz", body=empty_collection.to_json(),
        metadata=LearningContentMetadata(
            provider="test", model="test", model_version="1", generation_version="1",
            language="en", educational_level="college", subject="cs", syllabus="none",
            prompt_version="1", tags=("idempotency:ik1",), generation_id="1"
        ),
        statistics=LearningContentStatistics(character_count=0, word_count=0, estimated_tokens=0, processing_time_ms=0.0, confidence=1.0),
        created_at=datetime.now(UTC)
    )
    uow.learning.list_by_document = AsyncMock(return_value=[content_idempotent])
    res_dup = await use_case.execute(req)
    assert res_dup.status == "duplicate"


@pytest.mark.asyncio
async def test_add_quiz_creates_initial_content_with_chunk_collection() -> None:
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = MagicMock(user_id="user-456")
    authorization_service = AsyncMock()
    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value.__enter__.return_value = uow

    doc = MagicMock(user_id="user-456")
    uow.documents.get = AsyncMock(return_value=doc)
    uow.learning.list_by_document = AsyncMock(return_value=[])  # Empty initial content
    uow.learning.save = AsyncMock()

    from content.chunking import ChunkCollection
    chunk1 = MagicMock(id="chk-1")
    chunk2 = MagicMock(id="chk-2")
    chunk_collection = ChunkCollection(chunks=(chunk1, chunk2))
    uow.chunks.get_by_document = AsyncMock(return_value=chunk_collection)

    use_case = AddQuizQuestionUseCase(auth_service, authorization_service, uow_factory)
    req = AddQuizQuestionRequest(
        document_id="doc-456",
        token="valid_token",
        question="What is linear attention?",
        options=["O1", "O2", "O3", "O4"],
        correct_answer="O1",
        explanation="O1 is correct.",
        difficulty="medium",
        idempotency_key="ik_init_quiz_1",
    )

    res = await use_case.execute(req)
    assert res.status == "success"
    assert res.question_id is not None

    uow.learning.save.assert_called_once()
    saved_content = uow.learning.save.call_args[0][0]
    assert saved_content.source_chunk_ids == ("chk-1", "chk-2")
    assert saved_content.metadata.provider == "manual"
    assert saved_content.metadata.model == "manual"
    assert saved_content.metadata.educational_level == "general"
    assert saved_content.metadata.subject == "general"
    assert saved_content.metadata.syllabus == "general"
    assert "idempotency:ik_init_quiz_1" in saved_content.metadata.tags

