from unittest.mock import AsyncMock, MagicMock

import pytest

from application.learning.explain_mistake import ExplainMistakeRequest, ExplainMistakeUseCase
from application.learning.get_next_action import GetNextActionRequest, GetNextActionUseCase


@pytest.mark.asyncio
async def test_get_next_action() -> None:
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = MagicMock(user_id="user1")

    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value.__enter__.return_value = uow
    uow.documents.get = AsyncMock(return_value=MagicMock(user_id="user1"))

    uow.document_jobs.get = MagicMock(return_value=None)

    # Mock document job
    uow.analytics.has_completed_study = AsyncMock(return_value=False)
    uow.analytics.get_metrics = AsyncMock(
        return_value=MagicMock(quizzes_completed=0, average_quiz_accuracy=0.0)
    )

    use_case = GetNextActionUseCase(auth_service, uow_factory)
    res = await use_case.execute(GetNextActionRequest(document_id="doc1", token="token"))
    assert res.action.value == "study"


@pytest.mark.asyncio
async def test_explain_mistake() -> None:
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = MagicMock(user_id="user1")

    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value.__enter__.return_value = uow

    doc = MagicMock(user_id="user1")
    uow.documents.get = AsyncMock(return_value=doc)

    quiz_material = MagicMock()
    quiz_material.content_type.name = "quiz"
    quiz_material.body = '[{"id": "q1", "question": "Q?", "correct_answer": "o1", "options": [{"id": "o1", "text": "A"}, {"id": "o2", "text": "B"}]}]'

    uow.learning.list_by_document = AsyncMock(return_value=[quiz_material])

    provider = MagicMock()
    provider.generate.return_value = "AI explanation"

    use_case = ExplainMistakeUseCase(auth_service, uow_factory, provider)
    req = ExplainMistakeRequest(
        document_id="doc1", question_id="q1", selected_option_id="o2", token="token"
    )
    res = await use_case.execute(req)

    assert res.explanation == "AI explanation"
    provider.generate.assert_called_once()
