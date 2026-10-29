"""API contracts for retrieval-grounded question answering."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RagQueryRequest(BaseModel):
    """A bounded question over one or more indexed documents."""

    query: str = Field(..., min_length=1, max_length=4000)
    document_ids: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Documents to search. Empty means every ready document owned by the user.",
    )
    top_k: int = Field(6, ge=1, le=20)
    minimum_similarity: float = Field(0.25, ge=0.0, le=1.0)
    generate: bool = Field(
        True,
        description="When false this behaves as a retrieval-only request (no provider call).",
    )

    @model_validator(mode="after")
    def validate_query(self) -> RagQueryRequest:
        if not self.query.strip():
            raise ValueError("Query must contain non-whitespace text.")
        return self


class Citation(BaseModel):
    """A validated citation whose source was actually supplied to the model."""

    source_id: str
    chunk_id: str
    document_id: str
    document_title: str
    page_number: int | None = None
    section_title: str | None = None
    excerpt: str


class RetrievedSource(BaseModel):
    """A retrieved chunk, including transparent retrieval diagnostics."""

    source_id: str
    chunk_id: str
    document_id: str
    document_title: str
    chunk_index: int
    page_number: int | None = None
    section_title: str | None = None
    section_path: str | None = None
    text: str
    excerpt: str
    vector_score: float | None = None
    lexical_score: float | None = None
    fusion_score: float
    vector_rank: int | None = None
    lexical_rank: int | None = None


class RetrievalTimings(BaseModel):
    retrieval_ms: float
    generation_ms: float = 0.0
    total_ms: float


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class RagQueryResponse(BaseModel):
    status: Literal["answered", "insufficient_evidence", "error"]
    query: str
    answer: str
    grounded: bool
    citations: list[Citation] = Field(default_factory=list)
    sources: list[RetrievedSource] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    strategy: str = "hybrid_rrf"
    timings: RetrievalTimings
    usage: TokenUsage = Field(default_factory=TokenUsage)
    model: str | None = None
    provider: str | None = None
    cache_status: str = "not_supported"


class RetrievalOnlyResponse(BaseModel):
    """Retrieval playground response without generation."""

    query: str
    sources: list[RetrievedSource] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    strategy: str = "hybrid_rrf"
    timings: RetrievalTimings
