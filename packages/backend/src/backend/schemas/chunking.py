"""API contracts for the chunking laboratory."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ChunkPreviewRequest(BaseModel):
    """Preview a chunking configuration over supplied text or an indexed document."""

    text: str | None = Field(None, max_length=500_000)
    document_id: str | None = None
    chunk_size: int = Field(1200, ge=100, le=8000)
    chunk_overlap: int = Field(200, ge=0, le=4000)
    max_chunks: int = Field(40, ge=1, le=200)

    @model_validator(mode="after")
    def validate_source_and_overlap(self) -> ChunkPreviewRequest:
        if bool(self.text and self.text.strip()) == bool(self.document_id):
            raise ValueError("Provide exactly one of text or document_id.")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")
        return self


class PreviewChunk(BaseModel):
    index: int
    text: str
    character_count: int
    estimated_tokens: int
    page_number: int | None = None
    section_title: str | None = None
    overlap_prefix_characters: int = 0


class ChunkPreviewStats(BaseModel):
    chunk_count: int
    shown_chunk_count: int
    total_characters: int
    average_chunk_characters: float
    min_chunk_characters: int
    max_chunk_characters: int
    estimated_tokens: int
    chunk_size: int
    chunk_overlap: int
    strategy: str


class ChunkPreviewResponse(BaseModel):
    document_id: str | None = None
    source_characters: int
    chunks: list[PreviewChunk]
    stats: ChunkPreviewStats
    warnings: list[str] = Field(default_factory=list)


class ChunkConfig(BaseModel):
    chunk_size: int = Field(1200, ge=100, le=8000)
    chunk_overlap: int = Field(200, ge=0, le=4000)
    label: str | None = Field(None, max_length=80)

    @model_validator(mode="after")
    def validate_overlap(self) -> ChunkConfig:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")
        return self


class ChunkCompareRequest(BaseModel):
    text: str | None = Field(None, max_length=500_000)
    document_id: str | None = None
    configs: list[ChunkConfig] = Field(..., min_length=2, max_length=5)
    max_chunks: int = Field(12, ge=1, le=50)

    @model_validator(mode="after")
    def validate_source(self) -> ChunkCompareRequest:
        if bool(self.text and self.text.strip()) == bool(self.document_id):
            raise ValueError("Provide exactly one of text or document_id.")
        return self


class ChunkCompareResponse(BaseModel):
    document_id: str | None = None
    source_characters: int
    results: list[ChunkPreviewResponse]
    warnings: list[str] = Field(default_factory=list)
