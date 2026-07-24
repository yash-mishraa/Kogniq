import typing
import uuid
from datetime import UTC, datetime

from backend.core.exceptions import BackendError
from backend.schemas.document import DocumentInput, DocumentLifecycleState, DocumentProcessResult
from persistence.uow_factory import AbstractUnitOfWorkFactory
from pipeline.pipeline import DocumentIntelligencePipeline

from content.resource.checksum import Checksum, ChecksumAlgorithm
from content.resource.handle import ResourceHandle
from content.resource.lifecycle import LifecycleState
from content.resource.metadata import ResourceMetadata
from content.resource.source import ContentSource
from content.resource.stream import AbstractStreamReference


class BackendStreamReference(AbstractStreamReference):
    """Bridge between internal DocumentInput and Content layer AbstractStreamReference."""

    def __init__(self, doc_input: DocumentInput) -> None:
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

    async def process_document(
        self, doc_input: DocumentInput, job_id: str | None = None
    ) -> DocumentProcessResult:
        doc_id = str(uuid.uuid4())

        ext = ""
        if "." in doc_input.filename:
            ext = doc_input.filename.rsplit(".", 1)[1].lower()

        import hashlib

        checksum_value = hashlib.sha256(doc_input.content).hexdigest()

        handle = ResourceHandle(
            id=doc_id,
            filename=doc_input.filename,
            extension=ext,
            mime_type=doc_input.content_type,
            source=ContentSource.UPLOAD,
            checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value=checksum_value),
            size_bytes=doc_input.size_bytes,
            created_at=datetime.now(UTC),
            metadata=ResourceMetadata(
                attributes={
                    "original_path": doc_input.filename,
                    "content_type": doc_input.content_type,
                    "language": "en",
                }
            ),
            stream_reference=BackendStreamReference(doc_input),
            lifecycle_state=LifecycleState.REGISTERED,
        )

        try:
            result = await self.pipeline.run(handle, job_id=job_id)
        except Exception as e:
            raise BackendError("pipeline_execution_failed", str(e), status_code=500) from e

        # In Phase II, the pipeline stages handle persistence natively
        # So we just construct the result from the pipeline execution metadata

        metadata = result.get("metadata", {})
        stages = result.get("stages", {})

        processor = "Unknown"
        chunk_count = 0

        if "Ingestion" in stages and stages["Ingestion"].get("status") == "completed":
            data = stages["Ingestion"].get("data", {})
            doc_id = data.get("document_id", doc_id)
            processor = data.get("processor_name", "Unknown")
            chunk_count = data.get("chunk_count", 0)

        # Retrieve title from DB for result
        title = doc_input.filename
        try:
            with self.uow_factory.create() as uow:
                doc = await uow.documents.get(doc_id)
                if doc:
                    title = doc.title
        except Exception:
            pass

        return DocumentProcessResult(
            document_id=doc_id,
            filename=doc_input.filename,
            title=title,
            source=ContentSource.UPLOAD.name,
            processor=processor,
            chunk_count=chunk_count,
            processing_time_ms=metadata.get("total_processing_time_ms", 0),
            status=DocumentLifecycleState.READY,
            warnings=[],
        )

    async def list_documents(self) -> list[dict[str, typing.Any]]:
        with self.uow_factory.create() as uow:
            docs = await uow.documents.list()
            return [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "source": doc.source,
                    "status": "Ready",
                    "importDate": doc.created_at.isoformat(),
                }
                for doc in docs
            ]
