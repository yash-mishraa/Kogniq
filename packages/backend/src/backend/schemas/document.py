from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


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
    processor: str
    chunk_count: int
    embedding_count: int
    knowledge_concepts: int
    knowledge_relationships: int
    processing_time_ms: float
    status: str
    warnings: list[str]


class DocumentProcessResponse(BaseModel):
    """
    API Response Schema for document processing.
    """

    status: str = Field(..., description="Status of the processing")
    document_id: str = Field(..., description="Unique ID of the processed document")
    filename: str = Field(..., description="Original filename")
    processor: str = Field(..., description="The name of the content processor used")
    chunk_count: int = Field(..., description="Total semantic chunks extracted")
    embedding_count: int = Field(..., description="Total embeddings generated")
    knowledge_concepts: int = Field(..., description="Total knowledge concepts extracted")
    knowledge_relationships: int = Field(..., description="Total knowledge relationships extracted")
    processing_time_ms: float = Field(
        ..., description="Total pipeline execution time in milliseconds"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Non-fatal warnings during processing"
    )
