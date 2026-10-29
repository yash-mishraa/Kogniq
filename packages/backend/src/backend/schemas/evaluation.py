"""API contracts for reproducible retrieval and grounding evaluations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EvaluationCase(BaseModel):
    id: str | None = Field(None, max_length=80)
    question: str = Field(..., min_length=1, max_length=2000)
    expected_keywords: list[str] = Field(default_factory=list, max_length=20)
    expected_chunk_ids: list[str] = Field(default_factory=list, max_length=20)
    notes: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def require_expectation(self) -> EvaluationCase:
        if not self.expected_keywords and not self.expected_chunk_ids:
            raise ValueError("Each case needs expected_keywords or expected_chunk_ids.")
        return self


class EvaluationDataset(BaseModel):
    id: str
    name: str
    description: str
    builtin: bool = True


class RunEvaluationRequest(BaseModel):
    dataset_id: str = "custom"
    document_ids: list[str] = Field(default_factory=list, max_length=20)
    cases: list[EvaluationCase] = Field(..., min_length=1, max_length=25)
    top_k: int = Field(6, ge=1, le=20)
    minimum_similarity: float = Field(0.25, ge=0.0, le=1.0)
    generate: bool = Field(
        False,
        description="Run grounded generation and citation checks in addition to retrieval metrics.",
    )


class EvaluationCaseResult(BaseModel):
    case_id: str
    question: str
    hit: bool
    reciprocal_rank: float
    relevant_source_id: str | None = None
    source_count: int
    status: str
    citation_count: int
    grounded: bool
    latency_ms: float
    answer: str | None = None
    warnings: list[str] = Field(default_factory=list)


class EvaluationMetrics(BaseModel):
    retrieval_hit_rate: float
    mrr: float
    answer_rate: float
    grounded_rate: float
    citation_coverage: float
    avg_latency_ms: float
    cases: int
    hits: int


class RunEvaluationResponse(BaseModel):
    id: str
    dataset_id: str
    status: Literal["completed", "failed"]
    document_ids: list[str]
    generate: bool
    metrics: EvaluationMetrics
    details: list[EvaluationCaseResult]
    duration_ms: float
    created_at: str


class SuggestedCase(BaseModel):
    case: EvaluationCase
    rationale: str
