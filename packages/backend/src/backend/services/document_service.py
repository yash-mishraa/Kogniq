import typing
import uuid
from datetime import UTC, datetime

from backend.schemas.document import DocumentInput, DocumentLifecycleState, DocumentProcessResult
from persistence.uow_factory import AbstractUnitOfWorkFactory
from pipeline.pipeline import DocumentIntelligencePipeline

from application.document.commands import ProcessDocumentCommand
from content.resource.checksum import Checksum, ChecksumAlgorithm
from content.resource.handle import ResourceHandle
from content.resource.lifecycle import LifecycleState
from content.resource.metadata import ResourceMetadata
from content.resource.source import ContentSource
from content.resource.stream import AbstractStreamReference


class BackendStreamReference(AbstractStreamReference):
    """Bridge between internal DocumentInput and Content layer AbstractStreamReference."""

    def __init__(self, doc_input: ProcessDocumentCommand) -> None:
        self.doc_input = doc_input

    def open_stream(self) -> object:
        import io

        return io.BytesIO(self.doc_input.content)


class DocumentService:
    """
    Orchestrates document intelligence pipeline execution.
    No business logic, solely translates internal inputs to domain bounds.
    """

    def __init__(
        self, pipeline: DocumentIntelligencePipeline, uow_factory: AbstractUnitOfWorkFactory
    ) -> None:
        self.pipeline = pipeline
        self.uow_factory = uow_factory

    async def prepare_document(self, doc_input: ProcessDocumentCommand) -> DocumentProcessResult:
        doc_id = str(uuid.uuid4())
        created_at = datetime.now(UTC)

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
            title=doc_input.filename,
            source=ContentSource.UPLOAD.name,
            processor="Pending",
            chunk_count=0,
            processing_time_ms=0,
            status=DocumentLifecycleState.UPLOADED,
            warnings=[],
        )

    async def run_document_pipeline(
        self, doc_input: ProcessDocumentCommand, document_id: str
    ) -> None:
        ext = ""
        if "." in doc_input.filename:
            ext = doc_input.filename.rsplit(".", 1)[1].lower()

        import hashlib

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

        try:
            result = await self.pipeline.run(handle)
            # Check for warnings/errors in the result stages
            failed = False
            error_message = None
            if "stages" in result:
                for stage_name, stage_data in result["stages"].items():
                    if stage_data.get("status") == "failed":
                        failed = True
                        error_message = f"Stage {stage_name} failed: {stage_data.get('error')}"
                        break

            status = "Failed" if failed else "Ready"

            # 3. Update job status to Ready
            with self.uow_factory.create() as uow:
                job = uow.document_jobs.get(document_id)
                if job:
                    from persistence.models import DocumentJob

                    updated_job = DocumentJob(
                        id=job.id,
                        user_id=job.user_id,
                        filename=job.filename,
                        status=status,
                        created_at=job.created_at,
                        error_message=error_message,
                    )
                    uow.document_jobs.save(updated_job)

        except Exception as e:
            # Update job status to Error
            with self.uow_factory.create() as uow:
                job = uow.document_jobs.get(document_id)
                if job:
                    from persistence.models import DocumentJob

                    updated_job = DocumentJob(
                        id=job.id,
                        user_id=job.user_id,
                        filename=job.filename,
                        status="Error",
                        created_at=job.created_at,
                        error_message=str(e),
                    )
                    uow.document_jobs.save(updated_job)

    async def process_document(
        self, doc_input: DocumentInput, job_id: str | None = None
    ) -> DocumentProcessResult:
        from application.document.commands import ProcessDocumentCommand

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

    async def list_documents(self, user_id: str | None = None) -> list[dict[str, typing.Any]]:
        result = []
        with self.uow_factory.create() as uow:
            docs = await uow.documents.list(user_id=user_id)
            for doc in docs:
                result.append(
                    {
                        "id": doc.id,
                        "title": doc.title,
                        "source": doc.source,
                        "status": "Ready",
                        "importDate": doc.created_at.isoformat(),
                    }
                )

            jobs = uow.document_jobs.list_active(user_id=user_id)
            for job in jobs:
                result.append(
                    {
                        "id": job.id,
                        "title": job.filename,
                        "source": "upload",
                        "status": job.status,
                        "importDate": job.created_at.isoformat(),
                        "error": job.error_message or "",
                    }
                )

        return result
