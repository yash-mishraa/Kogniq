import contextlib
import json
from dataclasses import dataclass
from typing import Any

from backend.services.auth_service import AuthenticationService
from backend.services.authorization_service import AuthorizationService
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class GetLearningMaterialsRequest:
    document_id: str
    token: str


@dataclass(frozen=True)
class LearningMaterialItemResult:
    title: str
    body: Any


@dataclass(frozen=True)
class GetLearningMaterialsResponse:
    status: str
    materials: dict[str, LearningMaterialItemResult] | None


class GetLearningMaterialsUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        authorization_service: AuthorizationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.authorization_service = authorization_service
        self.uow_factory = uow_factory

    async def execute(self, request: GetLearningMaterialsRequest) -> GetLearningMaterialsResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from backend.core.exceptions import BackendError

            raise BackendError("unauthorized", "Invalid session", status_code=401)

        # Check document status and fetch materials
        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if not doc:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    "not_found", f"Document {request.document_id} not found", status_code=404
                )

            # Authorization can be added here (check if user owns document)
            if doc.user_id and doc.user_id != session.user_id:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    "unauthorized", "Not authorized to access this document", status_code=403
                )

            # The document exists, so we proceed to fetch materials.

            materials_list = await uow.learning.list_by_document(request.document_id)

            if not materials_list:
                return GetLearningMaterialsResponse(status="failed", materials=None)

            materials = {}
            for m in materials_list:
                key = m.content_type.name.lower()
                body = m.body

                if key in ["flashcards", "quiz"]:
                    with contextlib.suppress(json.JSONDecodeError):
                        body = json.loads(m.body)
                elif key == "study_guide":
                    key = "studyGuide"

                materials[key] = LearningMaterialItemResult(title=m.title, body=body)

            return GetLearningMaterialsResponse(status="completed", materials=materials)
