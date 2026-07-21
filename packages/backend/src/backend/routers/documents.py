from fastapi import APIRouter, Depends, File, Header, UploadFile

from application.document.commands import ProcessDocumentCommand
from application.document.process_document import ProcessDocumentUseCase
from backend.core.validators import DocumentValidator
from backend.dependencies import get_process_document_use_case
from backend.schemas.document import DocumentProcessResponse

documents_router = APIRouter(prefix="/documents", tags=["Documents"])


@documents_router.post("/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),  # noqa: B008
    x_user_id: str = Header("demo-user-1", alias="X-User-Id"),
    use_case: ProcessDocumentUseCase = Depends(get_process_document_use_case),  # noqa: B008
) -> DocumentProcessResponse:
    """
    Upload and process a document through the AI Intelligence Pipeline.
    """
    # 1. Validation
    DocumentValidator.validate(file)

    # 2. Map to Command
    content = await file.read()
    command = ProcessDocumentCommand(
        user_id=x_user_id,
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        content=content,
    )

    # 3. Process via Use Case
    result = await use_case.execute(command)

    # 4. Map to Response Schema
    return DocumentProcessResponse(
        status=result.status,
        document_id=result.document_id,
        filename=result.filename,
        processor=result.processor,
        chunk_count=result.chunk_count,
        embedding_count=result.embedding_count,
        knowledge_concepts=result.knowledge_concepts,
        knowledge_relationships=result.knowledge_relationships,
        processing_time_ms=result.processing_time_ms,
        warnings=list(result.warnings),
    )
