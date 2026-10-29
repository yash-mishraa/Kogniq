"""Reproducible evaluation of retrieval and citation grounding."""

from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.core.settings import settings
from backend.schemas.evaluation import (
    EvaluationCase,
    EvaluationCaseResult,
    EvaluationDataset,
    EvaluationMetrics,
    RunEvaluationRequest,
    RunEvaluationResponse,
    SuggestedCase,
)
from backend.schemas.rag import RagQueryRequest
from backend.services import index_state
from backend.services.rag_service import RagService
from persistence.uow_factory import AbstractUnitOfWorkFactory

_STOPWORDS = {
    "about",
    "after",
    "also",
    "because",
    "been",
    "before",
    "between",
    "could",
    "does",
    "from",
    "have",
    "into",
    "more",
    "most",
    "other",
    "over",
    "such",
    "than",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "under",
    "using",
    "very",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
}


def _connect() -> sqlite3.Connection:
    Path(settings.sqlite_database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.sqlite_database_path, timeout=30.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class EvaluationService:
    def __init__(self, rag_service: RagService, uow_factory: AbstractUnitOfWorkFactory) -> None:
        self.rag_service = rag_service
        self.uow_factory = uow_factory

    def datasets(self) -> list[EvaluationDataset]:
        return [
            EvaluationDataset(
                id="retrieval_smoke",
                name="Retrieval smoke",
                description=(
                    "A small, hand-authored set of questions with expected keywords or chunk IDs. "
                    "Use it to catch index regressions before changing embeddings or chunking."
                ),
            ),
            EvaluationDataset(
                id="custom",
                name="Custom cases",
                description="Your own questions and expected evidence.",
                builtin=False,
            ),
        ]

    async def suggest_cases(
        self, document_id: str, user_id: str, limit: int = 5
    ) -> list[SuggestedCase]:
        with self.uow_factory.create() as uow:
            document = await uow.documents.get(document_id)
            if not document:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    code="document_not_found",
                    message=f"Document '{document_id}' not found.",
                    status_code=404,
                )
            if document.user_id and document.user_id != user_id:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    code="forbidden",
                    message="Not authorized to access this document.",
                    status_code=403,
                )
            collection = await uow.chunks.get_by_document(document_id)
        chunks = list(collection.chunks) if collection else []
        suggestions: list[SuggestedCase] = []
        for chunk in chunks:
            if len(suggestions) >= limit:
                break
            if len(chunk.text.split()) < 20:
                continue
            words = [
                word.lower()
                for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{4,}", chunk.text)
                if word.lower() not in _STOPWORDS
            ]
            if not words:
                continue
            keywords = list(dict.fromkeys(words))[:5]
            topic = chunk.section_title or chunk.title or "this passage"
            suggestions.append(
                SuggestedCase(
                    case=EvaluationCase(
                        id=f"auto-{chunk.chunk_index}",
                        question=f"What does the source say about {topic}?",
                        expected_keywords=keywords,
                        expected_chunk_ids=[chunk.id],
                        notes="Deterministically suggested from a persisted chunk.",
                    ),
                    rationale=(
                        f"Chunk {chunk.chunk_index} is a substantial passage. The expected "
                        "keywords and chunk ID come from that chunk, not from a model."
                    ),
                )
            )
        return suggestions

    async def run(self, request: RunEvaluationRequest, user_id: str) -> RunEvaluationResponse:
        started = time.perf_counter()
        details: list[EvaluationCaseResult] = []
        hits = 0
        reciprocal_sum = 0.0
        answered = 0
        grounded = 0
        with_citations = 0

        status: str
        for index, case in enumerate(request.cases, start=1):
            case_started = time.perf_counter()
            rag_request = RagQueryRequest(
                query=case.question,
                document_ids=request.document_ids,
                top_k=request.top_k,
                minimum_similarity=request.minimum_similarity,
                generate=request.generate,
            )
            if request.generate:
                response = await self.rag_service.query(rag_request, user_id)
                sources = response.sources
                status = response.status
                answer = response.answer
                citations = response.citations
                case_grounded = response.grounded
                warnings = response.warnings
            else:
                retrieval = await self.rag_service.retrieve_only(rag_request, user_id)
                sources = retrieval.sources
                status = "retrieval_only"
                answer = None
                citations = []
                case_grounded = False
                warnings = retrieval.warnings

            relevant_rank: int | None = None
            relevant_source_id: str | None = None
            for rank, source in enumerate(sources, start=1):
                haystack = source.text.lower()
                keyword_hit = any(
                    keyword.lower() in haystack for keyword in case.expected_keywords
                )
                chunk_hit = source.chunk_id in case.expected_chunk_ids
                if keyword_hit or chunk_hit:
                    relevant_rank = rank
                    relevant_source_id = source.source_id
                    break

            hit = relevant_rank is not None
            if relevant_rank is not None:
                hits += 1
                reciprocal_sum += 1.0 / relevant_rank
            if request.generate and status == "answered":
                answered += 1
            if case_grounded:
                grounded += 1
            if citations:
                with_citations += 1

            details.append(
                EvaluationCaseResult(
                    case_id=case.id or f"case-{index}",
                    question=case.question,
                    hit=hit,
                    reciprocal_rank=round(1.0 / relevant_rank, 4) if relevant_rank else 0.0,
                    relevant_source_id=relevant_source_id,
                    source_count=len(sources),
                    status=status,
                    citation_count=len(citations),
                    grounded=case_grounded,
                    latency_ms=round((time.perf_counter() - case_started) * 1000.0, 2),
                    answer=answer,
                    warnings=warnings,
                )
            )

        total = len(details)
        answered_count = answered or 0
        metrics = EvaluationMetrics(
            retrieval_hit_rate=round(hits / total, 4) if total else 0.0,
            mrr=round(reciprocal_sum / total, 4) if total else 0.0,
            answer_rate=round(answered_count / total, 4) if total else 0.0,
            grounded_rate=round(grounded / answered_count, 4) if answered_count else 0.0,
            citation_coverage=(
                round(with_citations / answered_count, 4) if answered_count else 0.0
            ),
            avg_latency_ms=round(
                sum(detail.latency_ms for detail in details) / total, 2
            )
            if total
            else 0.0,
            cases=total,
            hits=hits,
        )
        duration_ms = (time.perf_counter() - started) * 1000.0
        run_id = str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()

        index_state.ensure_schema()
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO evaluation_runs (
                    id, user_id, dataset_id, document_id, status, metrics_json, details_json,
                    duration_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    user_id,
                    request.dataset_id,
                    request.document_ids[0] if len(request.document_ids) == 1 else None,
                    "completed",
                    json.dumps(metrics.model_dump()),
                    json.dumps([detail.model_dump() for detail in details]),
                    duration_ms,
                    created_at,
                ),
            )

        return RunEvaluationResponse(
            id=run_id,
            dataset_id=request.dataset_id,
            status="completed",
            document_ids=request.document_ids,
            generate=request.generate,
            metrics=metrics,
            details=details,
            duration_ms=round(duration_ms, 2),
            created_at=created_at,
        )

    def history(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        index_state.ensure_schema()
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT id, dataset_id, document_id, status, metrics_json, duration_ms, created_at
                FROM evaluation_runs WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (user_id, max(1, min(limit, 100))),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "dataset_id": row["dataset_id"],
                "document_id": row["document_id"],
                "status": row["status"],
                "metrics": json.loads(row["metrics_json"]),
                "duration_ms": row["duration_ms"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
