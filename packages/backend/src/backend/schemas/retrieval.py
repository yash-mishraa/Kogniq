from typing import Any

from pydantic import BaseModel, Field, model_validator


class RetrievalRequest(BaseModel):
    """Request payload for semantic retrieval."""

    document_id: str = Field(..., description="The ID of the document to search within.")
    query: str = Field(..., min_length=1, description="The semantic search query.")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of chunks to return.")
    minimum_similarity: float | None = Field(
        None, ge=0.0, le=1.0, description="Minimum similarity score threshold (0.0 to 1.0)."
    )

    @model_validator(mode="after")
    def validate_query_not_empty(self) -> "RetrievalRequest":
        if not self.query.strip():
            raise ValueError("Query string cannot be empty or only whitespace.")
        return self


class RetrievalResultItem(BaseModel):
    """An individual chunk matched during semantic retrieval."""

    chunk_id: str = Field(..., description="The ID of the chunk.")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0).")
    chunk_text: str = Field(..., description="The full hydrated text of the chunk.")
    chunk_index: int = Field(..., description="The index of the chunk within the document.")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Safe metadata from the chunk."
    )
    document_id: str = Field(..., description="The ID of the document.")


class RetrievalResponse(BaseModel):
    """Response payload returning matching chunks."""

    status: str = Field(default="completed")
    query: str = Field(..., description="The original search query.")
    document_id: str = Field(..., description="The queried document ID.")
    total_results: int = Field(..., description="Number of results returned.")
    results: list[RetrievalResultItem] = Field(
        ..., description="The ranked list of retrieved chunks."
    )
    processing_time_ms: float = Field(
        ..., description="Time taken to execute the search in milliseconds."
    )
    warnings: list[str] = Field(
        default_factory=list, description="Any warnings encountered during search."
    )
