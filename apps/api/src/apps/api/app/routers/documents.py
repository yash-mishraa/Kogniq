from backend.core.exceptions import BackendError
from backend.core.validators import DocumentValidator
from backend.dependencies import get_document_service, get_process_document_use_case
from backend.schemas.document import (
    DocumentLifecycleState,
    DocumentProcessResponse,
    DocumentResponse,
    DocumentDetailResponse,
)
from backend.services.document_service import DocumentService
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile

from application.document.commands import ProcessDocumentCommand
from application.document.process_document import ProcessDocumentUseCase
from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(tags=["Documents"])


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    current_user: CurrentUserDependency,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> list[DocumentResponse]:
    """
    List all documents in the workspace.
    """
    docs = await document_service.list_documents(user_id=current_user.user_id)
    return [DocumentResponse(**doc) for doc in docs]


@router.post("/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    current_user: CurrentUserDependency,
    background_tasks: BackgroundTasks,
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
        result = await use_case.prepare(command)

        # Add actual processing to background tasks
        async def run_in_background() -> None:
            await use_case.run_pipeline(command, result.document_id)

        background_tasks.add_task(run_in_background)
    except BackendError as e:
        raise APIError(status_code=e.status_code, code=e.code, message=e.message) from e

    # 4. Map to Response Schema
    return DocumentProcessResponse(
        status=DocumentLifecycleState.UPLOADED,
        document_id=result.document_id,
        filename=result.filename,
        title=result.title,
        source=result.source,
        processor=result.processor,
        chunk_count=result.chunk_count,
        processing_time_ms=result.processing_time_ms,
        warnings=list(result.warnings),
    )


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUserDependency,
) -> DocumentDetailResponse:
    """
    Retrieve a document and its full text content.
    """
    from backend.dependencies import get_uow_factory
    from fastapi import HTTPException

    uow_factory = get_uow_factory()
    with uow_factory.create() as uow:
        doc = await uow.documents.get(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.user_id and doc.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this document")

        content = ""
        if doc.pages:
            content = "\n\n".join(
                "\n".join(
                    block["text"] if isinstance(block, dict) else block.text
                    for block in page.blocks 
                    if (block.get("text") if isinstance(block, dict) else block.text)
                )
                for page in doc.pages if page.blocks
            )

        return DocumentDetailResponse(
            id=doc.id,
            title=doc.title,
            source=doc.source,
            status="Ready",
            importDate=doc.created_at.isoformat(),
            content=content,
        )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: CurrentUserDependency,
) -> dict[str, str]:
    """
    Delete a document and all its associated materials.
    """
    # Use the uow_factory directly or via document_service
    # Let's import get_uow_factory
    from backend.dependencies import get_uow_factory

    uow_factory = get_uow_factory()
    with uow_factory.create() as uow:
        # Check if document exists
        from fastapi import HTTPException

        doc = await uow.documents.get(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.user_id and doc.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this document")

        # Delete document. Since SQLite has ON DELETE CASCADE,
        # this will automatically delete chunks, concepts, relationships, and learning content.
        await uow.documents.delete(document_id)

    return {"status": "success", "message": f"Document {document_id} deleted"}


@router.post("/documents/recover", response_model=dict)
async def recover_failed_documents(
    current_user: CurrentUserDependency,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> dict:
    """
    Recover (cleanup) stalled or failed document ingestion jobs.
    """
    count = document_service.recover_failed_jobs(user_id=current_user.user_id)
    return {"status": "success", "recovered_count": count}
