from __future__ import annotations

import json
import logging
from typing import Any

from backend.core.exceptions import BackendError
from backend.core.validators import DocumentValidator
from backend.dependencies import (
    get_document_service,
    get_process_document_use_case,
    get_system_service,
)
from backend.schemas.document import (
    DocumentBlock,
    DocumentDetailResponse,
    DocumentLifecycleState,
    DocumentPage,
    DocumentProcessResponse,
    DocumentResponse,
    SemanticDocumentResponse,
)
from backend.services.document_service import DocumentService
from backend.services.system_service import SystemService
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import FileResponse

from application.document.commands import ProcessDocumentCommand
from application.document.process_document import ProcessDocumentUseCase
from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(tags=["Documents"])


def _map_pages(raw_pages: Any) -> list[DocumentPage]:
    pages: list[DocumentPage] = []
    for page in raw_pages or ():
        blocks = []
        for block in page.blocks:
            if isinstance(block, dict):
                blocks.append(
                    DocumentBlock(
                        id=block.get("block_id", ""),
                        text=block.get("text", ""),
                        type=block.get("block_type", "UNKNOWN"),
                        bbox=block.get("bbox"),
                        order=block.get("order", 0),
                    )
                )
            else:
                blocks.append(
                    DocumentBlock(
                        id=getattr(block, "block_id", ""),
                        text=getattr(block, "text", ""),
                        type=getattr(getattr(block, "block_type", None), "name", "UNKNOWN")
                        if hasattr(block, "block_type")
                        else "UNKNOWN",
                        bbox=getattr(block, "bbox", None),
                        order=getattr(block, "order", 0),
                    )
                )
        pages.append(
            DocumentPage(
                page_number=page.page_number,
                width=page.width,
                height=page.height,
                blocks=blocks,
            )
        )
    return pages


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    current_user: CurrentUserDependency,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> list[DocumentResponse]:
    """List every document with its authoritative index state."""
    docs = await document_service.list_documents(user_id=current_user.user_id)
    return [DocumentResponse(**doc) for doc in docs]


@router.post("/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    current_user: CurrentUserDependency,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),  # noqa: B008
    use_case: ProcessDocumentUseCase = Depends(get_process_document_use_case),  # noqa: B008
) -> DocumentProcessResponse:
    """Upload a document and start the ingestion/indexing pipeline."""
    try:
        DocumentValidator.validate(file)
    except BackendError as e:
        raise APIError(status_code=e.status_code, code=e.code, message=e.message) from e

    content = await file.read()
    command = ProcessDocumentCommand(
        user_id=current_user.user_id,
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        content=content,
    )

    try:
        result = await use_case.prepare(command)

        async def run_in_background() -> None:
            await use_case.run_pipeline(command, result.document_id)

        background_tasks.add_task(run_in_background)
    except BackendError as e:
        raise APIError(status_code=e.status_code, code=e.code, message=e.message) from e

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
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> DocumentDetailResponse:
    """Retrieve a document, its real index state, and its structured pages."""
    detail = await document_service.get_document(document_id, current_user.user_id)
    return DocumentDetailResponse(
        id=detail["id"],
        title=detail["title"],
        source=detail["source"],
        status=detail["status"],
        importDate=detail["importDate"],
        error=detail.get("error") or None,
        chunk_count=detail.get("chunk_count", 0),
        embedding_model=detail.get("embedding_model"),
        embedding_dimensions=detail.get("embedding_dimensions"),
        chunker_config=detail.get("chunker_config"),
        indexed_at=detail.get("indexed_at"),
        needs_reindex=detail.get("needs_reindex", False),
        pages=_map_pages(detail.get("pages")),
    )


@router.get("/documents/{document_id}/file")
async def get_document_file(
    document_id: str,
    current_user: CurrentUserDependency,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> FileResponse:
    """Retrieve the original uploaded file, preserving its stored filename/type."""
    path, filename, content_type = await document_service.upload_file(
        document_id, current_user.user_id
    )
    return FileResponse(path=path, media_type=content_type, filename=filename)


@router.get("/documents/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    current_user: CurrentUserDependency,
    limit: int = 100,
    offset: int = 0,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
    system_service: SystemService = Depends(get_system_service),  # noqa: B008
) -> dict[str, Any]:
    """Inspect the persisted chunks that retrieval can actually return."""
    detail = await document_service.get_document(document_id, current_user.user_id)
    chunks = system_service.document_chunks(
        document_id, limit=max(1, min(limit, 500)), offset=max(0, offset)
    )
    return {
        "document_id": document_id,
        "status": detail["status"],
        "chunk_count": detail.get("chunk_count", len(chunks)),
        "chunks": chunks,
    }


@router.post("/documents/{document_id}/retry")
async def retry_document(
    document_id: str,
    current_user: CurrentUserDependency,
    background_tasks: BackgroundTasks,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> dict[str, Any]:
    """Retry a failed ingestion using the stored original bytes."""
    # Validate ownership and source availability before returning 202 so the
    # UI can show an actionable error instead of a silent background failure.
    await document_service.upload_file(document_id, current_user.user_id)

    async def run() -> None:
        await document_service.retry_document(document_id, current_user.user_id)

    background_tasks.add_task(run)
    return {"status": "Processing", "document_id": document_id}


@router.post("/documents/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    current_user: CurrentUserDependency,
    background_tasks: BackgroundTasks,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> dict[str, Any]:
    """Rebuild the vector index for one document from its stored original bytes."""
    await document_service.upload_file(document_id, current_user.user_id)

    async def run() -> None:
        await document_service.reindex_document(document_id, current_user.user_id)

    background_tasks.add_task(run)
    return {"status": "Processing", "document_id": document_id}


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: CurrentUserDependency,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> dict[str, str]:
    """Delete a document, its chunks, index state, vectors, and stored upload."""
    await document_service.delete_document(document_id, current_user.user_id)
    return {"status": "success", "message": f"Document {document_id} deleted"}


@router.post("/documents/recover", response_model=dict)
async def recover_failed_documents(
    current_user: CurrentUserDependency,
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> dict[str, Any]:
    """Clean up stale/failed ingestion job records."""
    count = document_service.recover_failed_jobs(user_id=current_user.user_id)
    return {"status": "success", "recovered_count": count}


@router.get("/documents/{document_id}/semantics", response_model=SemanticDocumentResponse)
async def get_document_semantics(
    document_id: str,
    current_user: CurrentUserDependency,
) -> SemanticDocumentResponse:
    """Retrieve the active semantic structure (sections, figures) for a document."""
    from backend.dependencies import get_uow_factory
    from fastapi import HTTPException
    from pydantic import ValidationError

    uow_factory = get_uow_factory()
    with uow_factory.create() as uow:
        doc = await uow.documents.get(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.user_id and doc.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this document")

        active_semantics = await uow.semantics.get_active(document_id)
        if not active_semantics or active_semantics.status not in ("ready", "completed"):
            return SemanticDocumentResponse(
                document_id=document_id,
                status="unavailable",
                semantic_version=active_semantics.semantic_version if active_semantics else None,
                sections=[],
                figures=[],
            )

        try:
            data = json.loads(active_semantics.semantics_json)
            return SemanticDocumentResponse(
                document_id=document_id,
                status="ready",
                semantic_version=active_semantics.semantic_version,
                sections=data.get("sections", []),
                figures=data.get("figures", []),
            )
        except (json.JSONDecodeError, ValidationError, TypeError, AttributeError):
            logging.error(
                "Malformed semantic JSON for document %s, version %s",
                document_id,
                active_semantics.semantic_version,
            )
            return SemanticDocumentResponse(
                document_id=document_id,
                status="unavailable",
                semantic_version=active_semantics.semantic_version,
                sections=[],
                figures=[],
            )
