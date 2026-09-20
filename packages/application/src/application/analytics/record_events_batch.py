from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from backend.core.exceptions import BackendError
from backend.services.auth_service import AuthenticationService
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass
class EventPayload:
    event_id: str
    event_type: str
    resource_id: str
    data: dict[str, Any]
    section_id: str | None = None
    chunk_id: str | None = None
    idempotency_key: str | None = None

@dataclass
class RecordEventsBatchRequest:
    token: str
    events: list[EventPayload]

class RecordEventsBatchUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: RecordEventsBatchRequest) -> None:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError
            raise SessionExpiredError('Invalid session')

        user_id = session.user_id
        created_at = datetime.now(UTC)

        from domain.analytics.models import (
            ChunkViewedEvent,
            FlashcardReviewedEvent,
            LearnerEvent,
            QuizCompletedEvent,
            ResourceViewedEvent,
            StudySessionCompletedEvent,
        )

        if not request.events:
            return

        with self.uow_factory.create() as uow:
            # We must group by resource_id to verify ownership efficiently
            resource_ids = {e.resource_id for e in request.events}
            for rid in resource_ids:
                doc = await uow.documents.get(rid)
                if not doc:
                    raise BackendError('not_found', f'Resource {rid} not found', status_code=404)
                if doc.user_id and doc.user_id != user_id:
                    raise BackendError(
                        'unauthorized', 'Not authorized to access this resource', status_code=403
                    )
            learner_events = []
            for payload in request.events:
                # Normalize idempotency_key
                normalized_key = payload.idempotency_key
                if normalized_key is not None:
                    normalized_key = normalized_key.strip()
                    normalized_key = None if not normalized_key else f"{user_id}::{normalized_key}"

                # Basic mapping
                evt: LearnerEvent
                if payload.event_type == 'resource_viewed':
                    evt = ResourceViewedEvent(
                        event_id=payload.event_id,
                        user_id=user_id,
                        document_id=payload.resource_id,
                        event_type=payload.event_type,
                        event_data=payload.data,
                        created_at=created_at,
                        section_id=payload.section_id,
                        chunk_id=payload.chunk_id,
                        occurred_at=created_at,
                        idempotency_key=normalized_key,
                    )
                elif payload.event_type == 'chunk_viewed':
                    if not payload.section_id or not payload.chunk_id:
                        raise BackendError(
                            'bad_request', 'chunk_viewed missing IDs', status_code=400
                        )
                    evt = ChunkViewedEvent(
                        event_id=payload.event_id,
                        user_id=user_id,
                        document_id=payload.resource_id,
                        event_type=payload.event_type,
                        event_data=payload.data,
                        created_at=created_at,
                        section_id=payload.section_id,
                        chunk_id=payload.chunk_id,
                        occurred_at=created_at,
                        idempotency_key=normalized_key,
                    )
                elif payload.event_type == 'quiz_completed':
                    if 'score' not in payload.data or 'total_questions' not in payload.data:
                        raise BackendError(
                            'bad_request', 'quiz_completed requires score', status_code=400
                        )
                    score = payload.data['score']
                    total_questions = payload.data['total_questions']
                    if not isinstance(score, (int, float)) or isinstance(score, bool):
                        raise BackendError('bad_request', 'quiz numeric score required', status_code=400)
                    if not isinstance(total_questions, int) or isinstance(total_questions, bool) or total_questions <= 0:
                        raise BackendError('bad_request', 'quiz positive int total_questions required', status_code=400)
                    if score < 0:
                        raise BackendError('bad_request', 'score cannot be negative', status_code=400)
                    if score > total_questions:
                        raise BackendError('bad_request', 'score cannot exceed total_questions', status_code=400)
                    evt = QuizCompletedEvent(
                        event_id=payload.event_id,
                        user_id=user_id,
                        document_id=payload.resource_id,
                        event_type=payload.event_type,
                        event_data=payload.data,
                        created_at=created_at,
                        section_id=payload.section_id,
                        chunk_id=payload.chunk_id,
                        occurred_at=created_at,
                        idempotency_key=normalized_key,
                    )
                elif payload.event_type == 'flashcard_reviewed':
                    if 'card_id' not in payload.data or 'difficulty' not in payload.data:
                        raise BackendError(
                            'bad_request', 'flashcard_reviewed missing card', status_code=400
                        )
                    card_id = payload.data.get('card_id')
                    if not isinstance(card_id, str) or not card_id.strip():
                        raise BackendError('bad_request', 'card_id invalid', status_code=400)
                    
                    diff = payload.data['difficulty']
                    if not isinstance(diff, str) or diff not in ('easy', 'medium', 'hard', 'again'):
                        raise BackendError('bad_request', 'invalid difficulty', status_code=400)
                    evt = FlashcardReviewedEvent(
                        event_id=payload.event_id,
                        user_id=user_id,
                        document_id=payload.resource_id,
                        event_type=payload.event_type,
                        event_data=payload.data,
                        created_at=created_at,
                        section_id=payload.section_id,
                        chunk_id=payload.chunk_id,
                        occurred_at=created_at,
                        idempotency_key=normalized_key,
                    )
                elif payload.event_type == 'study_session_completed':
                    if 'completed_at' not in payload.data:
                        raise BackendError(
                            'bad_request', 'study_session missing completed_at', status_code=400
                        )
                    comp_at = payload.data['completed_at']
                    if not isinstance(comp_at, str):
                        raise BackendError('bad_request', 'completed_at invalid', status_code=400)
                    try:
                        datetime.fromisoformat(comp_at.replace("Z", "+00:00"))
                    except ValueError as e:
                        raise BackendError('bad_request', 'completed_at must be ISO-8601', status_code=400) from e
                    
                    evt = StudySessionCompletedEvent(
                        event_id=payload.event_id,
                        user_id=user_id,
                        document_id=payload.resource_id,
                        event_type=payload.event_type,
                        event_data=payload.data,
                        created_at=created_at,
                        section_id=payload.section_id,
                        chunk_id=payload.chunk_id,
                        occurred_at=created_at,
                        idempotency_key=normalized_key,
                    )
                else:
                    raise BackendError('bad_request', 'Unknown event', status_code=400)
                learner_events.append(evt)

            try:
                await uow.analytics.validate_event_relationships(learner_events)
            except ValueError as e:
                raise BackendError('invalid_reference', str(e), status_code=400) from e

            await uow.analytics.save_events(learner_events)
            
            # Recalculate Mastery Score for affected resources
            from domain.student.mastery_calculator import calculate_mastery
            
            for rid in resource_ids:
                events = await uow.analytics.list_events_by_resource(user_id, rid)
                new_state = calculate_mastery(events, user_id, rid)
                if new_state:
                    await uow.knowledge_states.save(new_state)
