from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class DocumentLifecycleState(StrEnum):
    UPLOADED = "Uploaded"
    EXTRACTING = "Extracting"
    NORMALIZING = "Normalizing"
    CHUNKING = "Chunking"
    PERSISTED = "Persisted"
    READY = "Ready"
    FAILED = "Failed"


@dataclass(frozen=True)
class DocumentInput:
    """
    Internal abstraction representing a document provided to the backend.
    Decouples the backend services from FastAPI's UploadFile or specific storage origins.
    """

    filename: str
    content_type: str
    size_bytes: int
    content: bytes

    def open_stream(self) -> Any:
        import io

        return io.BytesIO(self.content)


@dataclass
class DocumentProcessResult:
    """
    Internal backend model representing the result of processing a document.
    """

    document_id: str
    filename: str
    title: str
    source: str
    processor: str
    chunk_count: int
    processing_time_ms: float
    status: DocumentLifecycleState
    warnings: list[str]


class DocumentProcessResponse(BaseModel):
    """
    API Response Schema for document processing.
    """

    status: DocumentLifecycleState = Field(..., description="Lifecycle status of the processing")
    document_id: str = Field(..., description="Unique ID of the processed document")
    filename: str = Field(..., description="Original filename")
    title: str = Field(..., description="Canonical title of the document")
    source: str = Field(..., description="Source of the document")
    processor: str = Field(..., description="The name of the content processor used")
    chunk_count: int = Field(..., description="Total semantic chunks extracted")
    processing_time_ms: float = Field(
        ..., description="Total pipeline execution time in milliseconds"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Non-fatal warnings during processing"
    )


class DocumentResponse(BaseModel):
    """
    API Response Schema for retrieving a document.
    """

    id: str
    title: str
    source: str
    status: str
    importDate: str  # noqa: N815
