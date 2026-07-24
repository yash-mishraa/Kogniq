from backend.core.exceptions import BackendError
from backend.core.validators import DocumentValidator
from backend.dependencies import get_document_service, get_process_document_use_case
from backend.schemas.document import (
    DocumentLifecycleState,
    DocumentProcessResponse,
    DocumentResponse,
)
from backend.services.document_service import DocumentService
from fastapi import APIRouter, Depends, File, UploadFile

from application.document.commands import ProcessDocumentCommand
from application.document.process_document import ProcessDocumentUseCase
from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(tags=["Documents"])


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    _current_user: CurrentUserDependency,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> list[DocumentResponse]:
    """
    List all documents in the workspace.
    """
    # Later: Filter by current_user.user_id if document_service is updated to support it
    docs = await document_service.list_documents()
    return [DocumentResponse(**doc) for doc in docs]


@router.post("/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    current_user: CurrentUserDependency,
    file: UploadFile = File(...),  # noqa: B008
    use_case: ProcessDocumentUseCase = Depends(get_process_document_use_case),  # noqa: B008
) -> DocumentProcessResponse:
    """
    Upload and process a document through the AI Intelligence Pipeline.
    """
    # 1. Validation
    try:
        DocumentValidator.validate(file)
    except BackendError as e:
        raise APIError(status_code=e.status_code, code=e.code, message=e.message) from e

    # 2. Map to Command
    content = await file.read()
    command = ProcessDocumentCommand(
        user_id=current_user.user_id,
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        content=content,
    )

    # 3. Process via Use Case
    try:
        result = await use_case.execute(command)
    except BackendError as e:
        raise APIError(status_code=e.status_code, code=e.code, message=e.message) from e

    # 4. Map to Response Schema
    return DocumentProcessResponse(
        status=DocumentLifecycleState(result.status),
        document_id=result.document_id,
        filename=result.filename,
        title=result.title,
        source=result.source,
        processor=result.processor,
        chunk_count=result.chunk_count,
        processing_time_ms=result.processing_time_ms,
        warnings=list(result.warnings),
    )
