"""Document ingestion lifecycle and index administration.

The document row itself is not evidence that a document is usable. A document
is ``Ready`` only after parsing, chunking, embedding and vector persistence all
succeed, and only when ``document_index_state`` records that fact. Legacy
documents with chunks but no index state are surfaced as ``Unindexed`` and can
be explicitly reindexed rather than being silently treated as searchable.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import typing
import uuid
from datetime import UTC, datetime
from pathlib import Path

from backend.core.exceptions import BackendError
from backend.schemas.document import DocumentInput, DocumentLifecycleState, DocumentProcessResult
from backend.services import index_state
from persistence.uow_factory import AbstractUnitOfWorkFactory
from pipeline.pipeline import DocumentIntelligencePipeline

from application.document.commands import ProcessDocumentCommand
from content.resource.checksum import Checksum, ChecksumAlgorithm
from content.resource.handle import ResourceHandle
from content.resource.lifecycle import LifecycleState
from content.resource.metadata import ResourceMetadata
from content.resource.source import ContentSource
from content.resource.stream import AbstractStreamReference

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(os.environ.get("KOGNIQ_UPLOAD_DIR", "data/uploads"))
_SENTINEL_TITLES = {"", "untitled", "unknown", "document"}


class BackendStreamReference(AbstractStreamReference):
    """Bridge between internal DocumentInput and Content layer AbstractStreamReference."""

    def __init__(self, doc_input: ProcessDocumentCommand) -> None:
        self.doc_input = doc_input

    def open_stream(self) -> object:
        import io

        return io.BytesIO(self.doc_input.content)


def _filename_title(filename: str) -> str:
    name = Path(filename).name
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return stem.strip() or name or "Untitled document"


class DocumentService:
    """Orchestrates document intelligence pipeline execution and index state."""

    def __init__(
        self,
        pipeline: DocumentIntelligencePipeline,
        uow_factory: AbstractUnitOfWorkFactory,
        vector_store: typing.Any | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.uow_factory = uow_factory
        self.vector_store = vector_store

    # ------------------------------------------------------------------
    # Upload + ingestion
    # ------------------------------------------------------------------
    async def prepare_document(self, doc_input: ProcessDocumentCommand) -> DocumentProcessResult:
        doc_id = str(uuid.uuid4())
        created_at = datetime.now(UTC)

        index_state.mark_processing(doc_id, doc_input.user_id)

        with self.uow_factory.create() as uow:
            from persistence.models import DocumentJob

            job = DocumentJob(
                id=doc_id,
                user_id=doc_input.user_id,
                filename=doc_input.filename,
                status="Processing",
                created_at=created_at,
                error_message=None,
            )
            uow.document_jobs.save(job)

        return DocumentProcessResult(
            document_id=doc_id,
            filename=doc_input.filename,
            title=_filename_title(doc_input.filename),
            source=ContentSource.UPLOAD.name,
            processor="Pending",
            chunk_count=0,
            processing_time_ms=0,
            status=DocumentLifecycleState.UPLOADED,
            warnings=[],
        )

    def _store_upload(
        self, document_id: str, doc_input: ProcessDocumentCommand, *, overwrite: bool
    ) -> Path:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path = UPLOAD_DIR / f"{document_id}.upload"
        if overwrite or not file_path.exists():
            file_path.write_bytes(doc_input.content)
        meta_path = UPLOAD_DIR / f"{document_id}.meta.json"
        if overwrite or not meta_path.exists():
            meta_path.write_text(
                json.dumps(
                    {
                        "filename": doc_input.filename,
                        "content_type": doc_input.content_type,
                        "size_bytes": len(doc_input.content),
                        "stored_at": datetime.now(UTC).isoformat(),
                    }
                ),
                encoding="utf-8",
            )
        return file_path

    def _read_upload(self, document_id: str) -> tuple[bytes, str, str]:
        file_path = UPLOAD_DIR / f"{document_id}.upload"
        if not file_path.exists():
            # Legacy ingestion wrote PDFs directly under their document id.
            legacy_pdf = UPLOAD_DIR / f"{document_id}.pdf"
            if legacy_pdf.exists():
                file_path = legacy_pdf
            else:
                raise BackendError(
                    code="source_unavailable",
                    message=(
                        "The original file for this document is no longer available. "
                        "Upload it again to reindex it."
                    ),
                    status_code=409,
                )
        meta_path = UPLOAD_DIR / f"{document_id}.meta.json"
        filename = file_path.name
        content_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "text/plain"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                filename = str(meta.get("filename") or filename)
                content_type = str(meta.get("content_type") or content_type)
            except (OSError, json.JSONDecodeError):
                logger.warning("upload_metadata_unreadable", extra={"document_id": document_id})
        return file_path.read_bytes(), filename, content_type

    async def run_document_pipeline(
        self,
        doc_input: ProcessDocumentCommand,
        document_id: str,
        *,
        persist_upload: bool = True,
        clear_vectors: bool = False,
    ) -> None:
        ext = ""
        if "." in doc_input.filename:
            ext = doc_input.filename.rsplit(".", 1)[1].lower()

        self._store_upload(document_id, doc_input, overwrite=persist_upload)

        checksum_value = hashlib.sha256(doc_input.content).hexdigest()
        attrs: dict[str, str] = {
            "original_path": doc_input.filename,
            "content_type": doc_input.content_type,
            "language": "en",
        }
        if doc_input.user_id:
            attrs["user_id"] = doc_input.user_id

        handle = ResourceHandle(
            id=document_id,
            filename=doc_input.filename,
            extension=ext,
            mime_type=doc_input.content_type,
            source=ContentSource.UPLOAD,
            checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value=checksum_value),
            size_bytes=len(doc_input.content),
            created_at=datetime.now(UTC),
            metadata=ResourceMetadata(attributes=attrs),
            stream_reference=BackendStreamReference(doc_input),
            lifecycle_state=LifecycleState.REGISTERED,
        )

        index_state.mark_processing(document_id, doc_input.user_id)
        self._set_job_status(document_id, "Processing", None, doc_input)

        if clear_vectors and self.vector_store is not None:
            try:
                await asyncio.to_thread(
                    self.vector_store.delete_by_document, document_id
                )
            except Exception:
                logger.exception("vector_cleanup_failed", extra={"document_id": document_id})

        try:
            result = await self.pipeline.run(handle)
            failed = False
            error_message: str | None = None
            if isinstance(result, dict):
                for stage_name, stage_data in result.get("stages", {}).items():
                    if stage_data.get("status") == "failed":
                        failed = True
                        error_message = (
                            f"Stage {stage_name} failed: {stage_data.get('error')}"
                        )
                        break

            if failed:
                self._mark_failed(document_id, doc_input, error_message or "Unknown pipeline error")
                return

            stages = result.get("stages", {}) if isinstance(result, dict) else {}
            ingestion = stages.get("Ingestion", {}).get("data", {})
            embedding = stages.get("Embedding", {}).get("data", {})

            with self.uow_factory.create() as uow:
                document = await uow.documents.get(document_id)
                chunk_count = await uow.chunks.count_by_document(document_id)

            title = document.title if document and document.title else _filename_title(
                doc_input.filename
            )
            if title.strip().lower() in _SENTINEL_TITLES:
                title = _filename_title(doc_input.filename)

            chunker_config = str(
                embedding.get("chunker_config")
                or ingestion.get("chunker_config")
                or f"fixed:{os.environ.get('KOGNIQ_CHUNK_SIZE', '1200')}:"
                f"{os.environ.get('KOGNIQ_CHUNK_OVERLAP', '200')}"
            )
            index_state.mark_ready(
                document_id,
                doc_input.user_id,
                chunk_count=int(chunk_count or ingestion.get("chunk_count", 0)),
                embedding_model=str(
                    embedding.get("model_name")
                    or os.environ.get("KOGNIQ_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
                ),
                embedding_dimensions=int(embedding.get("dimensions") or 384),
                chunker_config=chunker_config,
            )
            self._set_job_status(document_id, "Ready", None, doc_input)
            logger.info(
                "document_indexed",
                extra={
                    "document_id": document_id,
                    "chunk_count": chunk_count,
                    "title": title,
                },
            )
        except Exception as exc:
            self._mark_failed(document_id, doc_input, str(exc))
            logger.exception("document_pipeline_failed", extra={"document_id": document_id})

    def _mark_failed(
        self, document_id: str, doc_input: ProcessDocumentCommand, error: str
    ) -> None:
        index_state.mark_failed(document_id, doc_input.user_id, error)
        self._set_job_status(document_id, "Error", error, doc_input)

    def _set_job_status(
        self,
        document_id: str,
        status: str,
        error: str | None,
        doc_input: ProcessDocumentCommand | None = None,
    ) -> None:
        from persistence.models import DocumentJob

        with self.uow_factory.create() as uow:
            job = uow.document_jobs.get(document_id)
            if job is None:
                if doc_input is None:
                    return
                job = DocumentJob(
                    id=document_id,
                    user_id=doc_input.user_id,
                    filename=doc_input.filename,
                    status=status,
                    created_at=datetime.now(UTC),
                    error_message=error,
                )
            else:
                job = DocumentJob(
                    id=job.id,
                    user_id=job.user_id,
                    filename=job.filename,
                    status=status,
                    created_at=job.created_at,
                    error_message=error,
                )
            uow.document_jobs.save(job)

    async def process_document(
        self,
        doc_input: DocumentInput,
        job_id: str | None = None,  # noqa: ARG002
    ) -> DocumentProcessResult:
        command = ProcessDocumentCommand(
            user_id=doc_input.user_id or "legacy-user",
            filename=doc_input.filename,
            size_bytes=doc_input.size_bytes,
            content=doc_input.content,
            content_type=doc_input.content_type,
        )
        result = await self.prepare_document(command)
        await self.run_document_pipeline(command, result.document_id)
        return result

    # ------------------------------------------------------------------
    # Read models
    # ------------------------------------------------------------------
    async def list_documents(self, user_id: str | None = None) -> list[dict[str, typing.Any]]:
        with self.uow_factory.create() as uow:
            documents = list(await uow.documents.list(user_id=user_id))
            jobs = list(uow.document_jobs.list_all(user_id=user_id))
            chunk_counts = {
                document.id: await uow.chunks.count_by_document(document.id)
                for document in documents
            }

        states = index_state.list_states(user_id=user_id)
        jobs_by_id = {job.id: job for job in jobs}
        result: list[dict[str, typing.Any]] = []
        seen: set[str] = set()

        for document in documents:
            seen.add(document.id)
            job = jobs_by_id.get(document.id)
            state = states.get(document.id)
            title = document.title
            if not title or title.strip().lower() in _SENTINEL_TITLES:
                title = _filename_title(job.filename if job else document.id)
            if state is not None:
                status = state.status
                error = state.error_message
                chunk_count = state.chunk_count
                indexed_at = state.indexed_at
                embedding_model = state.embedding_model
                dimensions = state.embedding_dimensions
                chunker_config = state.chunker_config
            elif job is not None and job.status in {"Processing", "Failed", "Error"}:
                status = "Failed" if job.status == "Error" else job.status
                error = job.error_message
                chunk_count = chunk_counts.get(document.id, 0)
                indexed_at = None
                embedding_model = None
                dimensions = None
                chunker_config = None
            else:
                # A legacy document row with chunks is not automatically ready:
                # there is no durable record that its vectors are compatible.
                status = "Unindexed"
                error = "No index state recorded. Reindex to make this document searchable."
                chunk_count = chunk_counts.get(document.id, 0)
                indexed_at = None
                embedding_model = None
                dimensions = None
                chunker_config = None
            result.append(
                {
                    "id": document.id,
                    "title": title,
                    "source": document.source,
                    "status": status,
                    "importDate": document.created_at.isoformat(),
                    "error": error or "",
                    "chunk_count": chunk_count,
                    "embedding_model": embedding_model,
                    "embedding_dimensions": dimensions,
                    "chunker_config": chunker_config,
                    "indexed_at": indexed_at,
                    "needs_reindex": status in {"Unindexed", "Failed"},
                }
            )

        for job in jobs:
            if job.id in seen:
                continue
            status = "Failed" if job.status == "Error" else job.status
            if status == "Ready":
                status = "Unindexed"
            result.append(
                {
                    "id": job.id,
                    "title": _filename_title(job.filename),
                    "source": "upload",
                    "status": status,
                    "importDate": job.created_at.isoformat(),
                    "error": job.error_message or "",
                    "chunk_count": 0,
                    "embedding_model": None,
                    "embedding_dimensions": None,
                    "chunker_config": None,
                    "indexed_at": None,
                    "needs_reindex": True,
                }
            )
        result.sort(key=lambda item: item["importDate"], reverse=True)
        return result

    async def get_document(self, document_id: str, user_id: str) -> dict[str, typing.Any]:
        with self.uow_factory.create() as uow:
            document = await uow.documents.get(document_id)
            if not document:
                raise BackendError(
                    code="document_not_found",
                    message=f"Document '{document_id}' not found.",
                    status_code=404,
                )
            if document.user_id and document.user_id != user_id:
                raise BackendError(
                    code="forbidden",
                    message="Not authorized to access this document.",
                    status_code=403,
                )
            job = uow.document_jobs.get(document_id)
            chunk_count = await uow.chunks.count_by_document(document_id)
        state = index_state.get_state(document_id)
        title = document.title
        if not title or title.strip().lower() in _SENTINEL_TITLES:
            title = _filename_title(job.filename if job else document.id)
        if state:
            status = state.status
            error = state.error_message or ""
        elif job and job.status in {"Processing", "Failed", "Error"}:
            status = "Failed" if job.status == "Error" else job.status
            error = job.error_message or ""
        else:
            status = "Unindexed"
            error = "No index state recorded. Reindex to make this document searchable."
        return {
            "id": document.id,
            "title": title,
            "source": document.source,
            "status": status,
            "importDate": document.created_at.isoformat(),
            "error": error,
            "chunk_count": state.chunk_count if state else chunk_count,
            "embedding_model": state.embedding_model if state else None,
            "embedding_dimensions": state.embedding_dimensions if state else None,
            "chunker_config": state.chunker_config if state else None,
            "indexed_at": state.indexed_at if state else None,
            "needs_reindex": status in {"Unindexed", "Failed"},
            "pages": document.pages,
        }

    # ------------------------------------------------------------------
    # Lifecycle administration
    # ------------------------------------------------------------------
    async def retry_document(self, document_id: str, user_id: str) -> dict[str, typing.Any]:
        document = await self._owned_document(document_id, user_id)
        content, filename, content_type = self._read_upload(document_id)
        command = ProcessDocumentCommand(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            content=content,
        )
        await self.run_document_pipeline(
            command, document_id, persist_upload=False, clear_vectors=True
        )
        return await self.get_document(document.id, user_id)

    async def reindex_document(self, document_id: str, user_id: str) -> dict[str, typing.Any]:
        return await self.retry_document(document_id, user_id)

    async def delete_document(self, document_id: str, user_id: str) -> None:
        document = await self._owned_document(document_id, user_id)
        if self.vector_store is not None:
            try:
                await asyncio.to_thread(
                    self.vector_store.delete_by_document, document.id
                )
            except Exception:
                logger.exception("vector_delete_failed", extra={"document_id": document.id})

        with self.uow_factory.create() as uow:
            await uow.documents.delete(document.id)
            uow.document_jobs.delete(document.id)
        index_state.delete_state(document.id)

        for suffix in (".upload", ".meta.json", ".pdf"):
            path = UPLOAD_DIR / f"{document.id}{suffix}"
            try:
                path.unlink(missing_ok=True)
            except OSError:
                logger.warning("upload_cleanup_failed", extra={"path": str(path)})

    async def _owned_document(self, document_id: str, user_id: str) -> typing.Any:
        with self.uow_factory.create() as uow:
            document = await uow.documents.get(document_id)
        if not document:
            raise BackendError(
                code="document_not_found",
                message=f"Document '{document_id}' not found.",
                status_code=404,
            )
        if document.user_id and document.user_id != user_id:
            raise BackendError(
                code="forbidden",
                message="Not authorized to access this document.",
                status_code=403,
            )
        return document

    async def upload_file(self, document_id: str, user_id: str) -> tuple[Path, str, str]:
        """Return the stored original file path, download name, and media type."""

        await self._owned_document(document_id, user_id)
        path = UPLOAD_DIR / f"{document_id}.upload"
        if not path.exists():
            path = UPLOAD_DIR / f"{document_id}.pdf"
        if not path.exists():
            raise BackendError(
                code="file_not_found",
                message="The original file is not available on disk.",
                status_code=404,
            )
        filename = path.name
        content_type = "application/pdf" if path.suffix.lower() == ".pdf" else "text/plain"
        meta_path = UPLOAD_DIR / f"{document_id}.meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                filename = str(meta.get("filename") or filename)
                content_type = str(meta.get("content_type") or content_type)
            except (OSError, json.JSONDecodeError):
                pass
        return path, filename, content_type

    def recover_failed_jobs(self, user_id: str) -> int:
        """Delete stale tracking records without pretending the upload succeeded."""

        recovered_count = 0
        from datetime import timedelta

        now = datetime.now(UTC)
        with self.uow_factory.create() as uow:
            jobs = uow.document_jobs.list_active(user_id=user_id)
            for job in jobs:
                stale = job.status == "Processing" and (now - job.created_at) > timedelta(hours=1)
                if job.status in {"Error", "Failed"} or stale:
                    uow.document_jobs.delete(job.id)
                    recovered_count += 1
                    logger.info(
                        "recovered_ingestion_job",
                        extra={
                            "job_id": job.id,
                            "previous_state": job.status,
                            "stale": stale,
                        },
                    )
        return recovered_count
