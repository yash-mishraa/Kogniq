from fastapi import APIRouter, Depends, File, UploadFile

from backend.core.validators import DocumentValidator
from backend.dependencies import get_document_service
from backend.schemas.document import DocumentInput, DocumentProcessResponse
from backend.services.document_service import DocumentService

documents_router = APIRouter(prefix="/documents", tags=["Documents"])


@documents_router.post("/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),  # noqa: B008
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> DocumentProcessResponse:
    """
    Upload and process a document through the AI Intelligence Pipeline.
    """
    # 1. Validation
    DocumentValidator.validate(file)

    # 2. Extract into safe DocumentInput
    content = await file.read()
    doc_input = DocumentInput(
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        content=content,
    )

    # 3. Process via Service
    result = await document_service.process_document(doc_input)

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
        warnings=result.warnings,
    )
