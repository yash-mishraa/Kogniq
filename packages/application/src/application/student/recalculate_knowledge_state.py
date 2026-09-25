from dataclasses import dataclass
from domain.student.mastery_calculator import calculate_mastery
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class RecalculateKnowledgeStateRequest:
    user_id: str
    resource_id: str


@dataclass(frozen=True)
class RecalculateKnowledgeStateResponse:
    success: bool
    mastery_score: float | None


class RecalculateKnowledgeStateUseCase:
    def __init__(
        self,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.uow_factory = uow_factory

    async def execute(self, request: RecalculateKnowledgeStateRequest) -> RecalculateKnowledgeStateResponse:
        """
        Fetches all events for a user and resource, runs the deterministic mastery calculation,
        and upserts the resulting KnowledgeState.
        """
        with self.uow_factory.create() as uow:
            # 1. Fetch events
            events = await uow.analytics.list_events_by_resource(request.user_id, request.resource_id)
            
            # 2. Calculate mastery
            new_state = calculate_mastery(events, request.user_id, request.resource_id)
            
            # 3. Upsert state
            if new_state:
                await uow.knowledge_states.save(new_state)
            else:
                # If there are NO events at all, maybe we should not have a knowledge state,
                # or perhaps keep it as 0.0? The calculate_mastery returns None if NO events exist.
                # If it's None, it means the user has zero footprint on this resource. 
                # We could delete the state or leave it alone. The simplest is to just do nothing.
                pass
                
            uow.commit()

        return RecalculateKnowledgeStateResponse(
            success=True,
            mastery_score=new_state.mastery_score if new_state else None
        )
