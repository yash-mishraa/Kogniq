import dataclasses
import logging
import re
from typing import Any

from persistence.uow_factory import AbstractUnitOfWorkFactory

from content.chunking.collection import ChunkCollection
from pipeline.interfaces import PipelineContext, PipelineStage, RetryPolicy, StageResult

logger = logging.getLogger(__name__)


class NoRetryPolicy(RetryPolicy):
    @property
    def max_retries(self) -> int:
        return 0

    @property
    def delay_seconds(self) -> int:
        return 0


class SemanticEnrichmentStageResult(StageResult):
    def __init__(self, success: bool, data: dict[str, Any], error: str | None = None) -> None:
        self._success = success
        self._data = data
        self._error = error

    @property
    def success(self) -> bool:
        return self._success

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def error(self) -> str | None:
        return self._error


class SemanticEnrichmentStage(PipelineStage):
    """
    Deterministically maps the chunks from IngestionStage to the semantic sections
    and figures extracted during SemanticExtractionStage.
    """

    def __init__(self, uow_factory: AbstractUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory
        self._retry_policy = NoRetryPolicy()

    @property
    def stage_name(self) -> str:
        return "SemanticEnrichment"

    async def can_skip(self, context: PipelineContext) -> bool:
        chunk_collection = context.get("chunk_collection")
        return not chunk_collection or not chunk_collection.chunks

    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

    async def execute(self, context: PipelineContext) -> StageResult:
        chunk_collection: ChunkCollection | None = context.get("chunk_collection")
        if not chunk_collection:
            return SemanticEnrichmentStageResult(False, {}, "No chunk_collection provided")

        document_id = context.get("document_id")
        if not document_id:
            # Fallback for older tests
            document_id = getattr(context, "document_id", None)
            if not document_id:
                return SemanticEnrichmentStageResult(False, {}, "document_id not set in context")

        # 1. Fetch active semantics
        active_semantics = None
        try:
            with self._uow_factory.create() as uow:
                active_semantics = await uow.semantics.get_active(document_id)
        except Exception as e:
            logger.warning(f"Failed to fetch semantics for enrichment: {e}")

        if not active_semantics:
            return SemanticEnrichmentStageResult(
                True, {"message": "No active semantics found for enrichment"}
            )

        import json

        try:
            semantic_data = json.loads(active_semantics.semantics_json)
        except Exception as e:
            logger.warning(f"Malformed semantics JSON for {document_id}: {e}")
            return SemanticEnrichmentStageResult(True, {"warning": "Malformed semantics JSON"})

        sections = semantic_data.get("sections", [])
        figures = semantic_data.get("figures", [])

        # Build hierarchy map
        section_by_id = {s["id"]: s for s in sections}

        def get_path(sec_id: str | None) -> str:
            path: list[str] = []
            curr = sec_id
            while curr:
                s = section_by_id.get(curr)
                if not s:
                    break
                path.insert(0, s["title"])
                curr = s.get("parent_id")
            return " > ".join(path)

        def clean_text(t: str) -> str:
            return re.sub(r"\s+", " ", t).strip().lower()

        for s in sections:
            s["clean"] = clean_text(s["title"])
            s["path"] = get_path(s["id"])

        for f in figures:
            f["clean"] = clean_text(f.get("caption", "")) if f.get("caption") else ""

        enriched_chunks = []
        current_section = None
        section_idx = 0

        for chunk in chunk_collection.chunks:
            chunk_clean = clean_text(chunk.text)

            # Map Section
            lookahead = 3
            best_new_section = None
            best_new_idx = section_idx

            for offset in range(lookahead):
                idx = section_idx + offset
                if (
                    idx < len(sections)
                    and sections[idx].get("page_number", 0) <= (chunk.page_number or 0) + 1
                    and sections[idx]["clean"] in chunk_clean
                ):
                    best_new_section = sections[idx]
                    best_new_idx = idx

            if best_new_section:
                current_section = best_new_section
                section_idx = best_new_idx + 1

            # Map Figure
            mapped_figure = None
            for f in figures:
                if f["clean"] and (f["clean"] in chunk_clean or f["clean"][:30] in chunk_clean):
                    mapped_figure = f
                    break

            # Create enriched chunk
            kwargs = {
                "section_id": current_section["id"] if current_section else None,
                "section_title": current_section["title"] if current_section else None,
                "section_path": current_section["path"] if current_section else None,
                "figure_id": mapped_figure["id"] if mapped_figure else None,
                "figure_number": mapped_figure.get("figure_number") if mapped_figure else None,
            }

            new_meta = dataclasses.replace(
                chunk.metadata,
                **{k: v for k, v in kwargs.items() if hasattr(chunk.metadata, k)},  # type: ignore
            )

            # Create enriched chunk (fields are on both Chunk and metadata)
            enriched = dataclasses.replace(
                chunk,
                metadata=new_meta,
                **{k: v for k, v in kwargs.items() if hasattr(chunk, k)},  # type: ignore
            )
            enriched_chunks.append(enriched)

        # Update context with enriched chunks
        new_collection = ChunkCollection(chunks=tuple(enriched_chunks))
        context.set("chunk_collection", new_collection)

        # Save enriched chunks back to SQLite
        try:
            with self._uow_factory.create() as uow:
                # We need to use replace/update semantics. Fortunately,
                # SQLiteChunkRepository.save() rewrites document_chunks rows.
                await uow.chunks.save(new_collection)
                uow.commit()
        except Exception as e:
            logger.warning(f"Failed to persist enriched chunks: {e}")

        return SemanticEnrichmentStageResult(True, {"enriched_chunks": len(enriched_chunks)})
