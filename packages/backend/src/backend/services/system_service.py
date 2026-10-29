"""Operational read models for the RAG console."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from backend.core.settings import settings
from backend.services import index_state


def _connect() -> sqlite3.Connection:
    Path(settings.sqlite_database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.sqlite_database_path, timeout=30.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class SystemService:
    def __init__(self, vector_store: Any | None = None) -> None:
        self.vector_store = vector_store

    def vector_count(self) -> int | None:
        if self.vector_store is None:
            return None
        try:
            return int(self.vector_store.count())
        except Exception:
            return None

    async def overview(self, user_id: str) -> dict[str, Any]:
        index_state.ensure_schema()
        with _connect() as conn:
            document_rows = conn.execute(
                "SELECT id, title, created_at FROM documents WHERE user_id = ?", (user_id,)
            ).fetchall()
            chunk_count = conn.execute(
                """
                SELECT COUNT(*) AS count FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE d.user_id = ?
                """,
                (user_id,),
            ).fetchone()["count"]
            state_rows = conn.execute(
                "SELECT status, COUNT(*) AS count FROM document_index_state WHERE user_id = ? "
                "GROUP BY status",
                (user_id,),
            ).fetchall()
            recent_cutoff = (datetime.now(UTC) - timedelta(days=7)).isoformat()
            query_stats = conn.execute(
                """
                SELECT COUNT(*) AS count,
                       AVG(total_ms) AS avg_total_ms,
                       AVG(retrieval_ms) AS avg_retrieval_ms,
                       AVG(generation_ms) AS avg_generation_ms,
                       SUM(citation_count) AS citations,
                       SUM(CASE WHEN status = 'answered' THEN 1 ELSE 0 END) AS answered,
                       SUM(
                           CASE WHEN status = 'insufficient_evidence' THEN 1 ELSE 0 END
                       ) AS insufficient
                FROM query_logs
                WHERE user_id = ? AND created_at >= ?
                """,
                (user_id, recent_cutoff),
            ).fetchone()
            recent_queries = conn.execute(
                """
                SELECT id, query_text, status, total_ms, retrieval_ms, generation_ms,
                       citation_count, citations_valid, model, created_at
                FROM query_logs WHERE user_id = ?
                ORDER BY created_at DESC LIMIT 8
                """,
                (user_id,),
            ).fetchall()
            eval_count = conn.execute(
                "SELECT COUNT(*) AS count FROM evaluation_runs WHERE user_id = ?", (user_id,)
            ).fetchone()["count"]

        states = {row["status"]: row["count"] for row in state_rows}
        indexed_documents = int(states.get(index_state.READY, 0))
        vector_document_ids: set[str] = set()
        vector_count: int | None = None
        vector_error: str | None = None
        if self.vector_store is not None:
            try:
                vector_count = int(self.vector_store.count())
                vector_document_ids = set(self.vector_store.document_ids())
            except Exception as exc:
                vector_error = str(exc)

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "documents": {
                "total": len(document_rows),
                "ready": indexed_documents,
                "processing": int(states.get(index_state.PROCESSING, 0)),
                "failed": int(states.get(index_state.FAILED, 0)),
                "unindexed": max(0, len(document_rows) - indexed_documents),
                "chunks": int(chunk_count),
            },
            "index": {
                "provider": settings.vector_store_provider,
                "collection": settings.chroma_collection
                if settings.vector_store_provider == "chroma"
                else settings.qdrant_collection,
                "vector_count": vector_count,
                "indexed_documents": len(vector_document_ids),
                "embedding_model": index_state.get_index_metadata("embedding_model")
                or "all-MiniLM-L6-v2",
                "embedding_dimensions": int(
                    index_state.get_index_metadata("embedding_dimensions") or 384
                ),
                "chunker_config": index_state.get_index_metadata("chunker_config"),
                "metadata": index_state.all_index_metadata(),
                "error": vector_error,
            },
            "queries_7d": {
                "count": int(query_stats["count"] or 0),
                "answered": int(query_stats["answered"] or 0),
                "insufficient": int(query_stats["insufficient"] or 0),
                "avg_total_ms": round(float(query_stats["avg_total_ms"] or 0), 2),
                "avg_retrieval_ms": round(float(query_stats["avg_retrieval_ms"] or 0), 2),
                "avg_generation_ms": round(float(query_stats["avg_generation_ms"] or 0), 2),
                "citations": int(query_stats["citations"] or 0),
            },
            "evaluation_runs": int(eval_count),
            "recent_queries": [dict(row) for row in recent_queries],
            "capabilities": {
                "hybrid_retrieval": True,
                "fts5": self._fts_available(),
                "prompt_cache": False,
                "prompt_cache_note": (
                    "Kogniq does not claim provider-side prompt caching. Gemini's hosted "
                    "implicit caching is provider-managed and is not a Kogniq feature."
                ),
            },
        }

    def _fts_available(self) -> bool:
        try:
            with _connect() as conn:
                conn.execute("SELECT 1 FROM document_chunks_fts LIMIT 1")
            return True
        except sqlite3.OperationalError:
            return False

    async def ready(self) -> dict[str, Any]:
        index_state.ensure_schema()
        checks: dict[str, Any] = {}
        try:
            with _connect() as conn:
                conn.execute("SELECT 1").fetchone()
            checks["database"] = {"ok": True}
        except Exception as exc:
            checks["database"] = {"ok": False, "error": str(exc)}
        checks["lexical_index"] = {"ok": self._fts_available()}
        vector_count = self.vector_count()
        checks["vector_index"] = {
            "ok": vector_count is not None,
            "count": vector_count,
        }
        try:
            from backend.dependencies import _get_configured_provider

            prov = _get_configured_provider()
            prov_health = prov.health() if hasattr(prov, "health") else {"status": "healthy"}
            primary = prov_health.get("primary", prov_health)
            is_ok = primary.get("status") in ("healthy", "circuit_open") or prov_health.get("status") in ("healthy", "circuit_open")
            checks["generation_provider"] = {
                "ok": is_ok,
                **prov_health,
            }
        except Exception as exc:
            checks["generation_provider"] = {"ok": False, "error": str(exc)}
        return {
            "ready": all(check.get("ok", False) for check in checks.values()),
            "checks": checks,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def recent_queries(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        index_state.ensure_schema()
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT id, kind, query_text, document_ids_json, strategy, status, error_category,
                       retrieval_ms, generation_ms, total_ms, candidate_count, selected_count,
                       prompt_tokens, completion_tokens, total_tokens, model, provider,
                       citation_count, citations_valid, cache_status, created_at
                FROM query_logs WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (user_id, max(1, min(limit, 200))),
            ).fetchall()
        return [dict(row) for row in rows]

    def document_chunks(
        self, document_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT id, chunk_index, text, title, page_number, section_title,
                       section_id, created_at, metadata_json
                FROM document_chunks WHERE document_id = ?
                ORDER BY chunk_index LIMIT ? OFFSET ?
                """,
                (document_id, max(1, min(limit, 500)), max(0, offset)),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "chunk_index": row["chunk_index"],
                "text": row["text"],
                "title": row["title"],
                "page_number": row["page_number"],
                "section_title": row["section_title"],
                "section_id": row["section_id"],
                # The persisted schema stores section_id, not a materialised
                # breadcrumb path. Keep the contract field present but honest.
                "section_path": None,
                "created_at": row["created_at"],
                "character_count": len(row["text"] or ""),
                "estimated_tokens": len(row["text"] or "") // 4,
            }
            for row in rows
        ]
