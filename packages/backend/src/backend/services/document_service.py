import uuid
from datetime import UTC, datetime

from backend.core.exceptions import BackendError
from backend.schemas.document import DocumentInput, DocumentProcessResult
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
        return self.doc_input.open_stream()


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

    async def process_document(self, doc_input: DocumentInput) -> DocumentProcessResult:
        doc_id = str(uuid.uuid4())

        # We need a proper extension format for the content registry (.pdf -> pdf)
        # Actually content registry normalizes to lower case without dot or with dot?
        # The handle requires the extension.
        ext = ""
        if "." in doc_input.filename:
            ext = doc_input.filename.rsplit(".", 1)[1].lower()

        handle = ResourceHandle(
            id=doc_id,
            filename=doc_input.filename,
            extension=ext,
            mime_type=doc_input.content_type,
            source=ContentSource.UPLOAD,
            # In reality, compute checksum
            checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="dummy"),
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
            result = self.pipeline.run(handle)
        except Exception as e:
            # We catch any exception that could escape the pipeline
            # and translate it to our canonical BackendError.
            raise BackendError("pipeline_execution_failed", str(e), status_code=500) from e

        # Map PipelineResult to our internal DocumentProcessResult
        # Persist domain objects
        try:
            with self.uow_factory.create() as uow:
                await uow.documents.save(result.content.document)
                await uow.chunks.save(result.content.chunks)
                await uow.knowledge.save(doc_id, result.knowledge.extraction_result.graph)
        except Exception as e:
            raise BackendError(
                "persistence_failed", f"Failed to persist pipeline results: {e}", status_code=500
            ) from e

        return DocumentProcessResult(
            document_id=doc_id,
            filename=doc_input.filename,
            processor=result.metadata.processor_name,
            chunk_count=result.content.chunks.total_chunks,
            embedding_count=len(result.embeddings.collection.embeddings),
            knowledge_concepts=result.knowledge.extraction_result.graph.concept_count,
            knowledge_relationships=result.knowledge.extraction_result.graph.relationship_count,
            processing_time_ms=result.metadata.total_processing_time_ms,
            status="completed",
            warnings=[],
        )
