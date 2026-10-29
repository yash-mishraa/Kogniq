"""Chunking laboratory: deterministic previews and configuration comparisons.

The production ingestion path and this service share the same
``FixedSizeChunkStrategy``. That matters: a chunking preview is only useful if
it describes the chunks that ingestion would actually write.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from backend.core.exceptions import BackendError
from backend.schemas.chunking import (
    ChunkCompareRequest,
    ChunkCompareResponse,
    ChunkConfig,
    ChunkPreviewRequest,
    ChunkPreviewResponse,
    ChunkPreviewStats,
    PreviewChunk,
)
from persistence.uow_factory import AbstractUnitOfWorkFactory

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.strategies.fixed_size import FixedSizeChunkStrategy
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.page import NormalizedPage


def _blocks_text(blocks: tuple[NormalizedBlock, ...]) -> list[str]:
    parts: list[str] = []
    for block in blocks:
        if block.text and block.text.strip():
            parts.append(block.text.strip())
        if block.children:
            parts.extend(_blocks_text(block.children))
    return parts


def document_text(document: Any) -> str:
    """Return the same reading-order text the chunker sees."""

    paragraphs: list[str] = []
    for page in document.pages:
        paragraphs.extend(_blocks_text(page.blocks))
    return "\n".join(paragraphs).strip()


def _overlap_prefix(previous: str, current: str) -> int:
    """Length of the longest suffix/prefix overlap between adjacent chunks."""

    limit = min(len(previous), len(current), 2000)
    for size in range(limit, 0, -1):
        if previous.endswith(current[:size]):
            return size
    return 0


class ChunkingService:
    def __init__(self, uow_factory: AbstractUnitOfWorkFactory) -> None:
        self.uow_factory = uow_factory

    async def _resolve_source(
        self, *, text: str | None, document_id: str | None, user_id: str
    ) -> tuple[str, str | None]:
        if text is not None:
            return text, None
        assert document_id is not None
        with self.uow_factory.create() as uow:
            document = await uow.documents.get(document_id)
        if not document:
            raise BackendError(
                code="document_not_found",
                message=f"Document '{document_id}' not found.",
                status_code=404,
            )
        if document.user_id and document.user_id != user_id:
            raise BackendError(
                code="forbidden",
                message="Not authorized to access this document.",
                status_code=403,
            )
        return document_text(document), document_id

    @staticmethod
    def _chunk_text(
        text: str,
        *,
        chunk_size: int,
        chunk_overlap: int,
        document_id: str,
    ) -> ChunkCollection:
        document = NormalizedDocument(
            id=document_id,
            title="Chunk preview",
            source="chunking-lab",
            checksum="preview",
            version="preview",
            created_at=datetime.now(UTC),
            pages=(
                NormalizedPage(
                    page_number=1,
                    blocks=(
                        NormalizedBlock(
                            block_id="preview-block",
                            block_type=BlockType.PARAGRAPH,
                            text=text,
                            order=0,
                        ),
                    ),
                ),
            ),
        )
        return FixedSizeChunkStrategy(
            max_characters=chunk_size, overlap_characters=chunk_overlap
        ).chunk(document)

    @staticmethod
    def _map_preview(
        collection: ChunkCollection,
        *,
        source_characters: int,
        chunk_size: int,
        chunk_overlap: int,
        max_chunks: int,
        document_id: str | None,
    ) -> ChunkPreviewResponse:
        chunks = list(collection.chunks)
        shown: list[PreviewChunk] = []
        previous_text = ""
        for chunk in chunks[:max_chunks]:
            shown.append(
                PreviewChunk(
                    index=chunk.chunk_index,
                    text=chunk.text,
                    character_count=len(chunk.text),
                    estimated_tokens=max(1, len(chunk.text) // 4),
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    overlap_prefix_characters=(
                        _overlap_prefix(previous_text, chunk.text) if previous_text else 0
                    ),
                )
            )
            previous_text = chunk.text

        lengths = [len(chunk.text) for chunk in chunks] or [0]
        warnings: list[str] = []
        if len(chunks) > max_chunks:
            warnings.append(
                f"Showing {max_chunks} of {len(chunks)} chunks. "
                "Increase max_chunks to inspect more."
            )
        if not chunks:
            warnings.append("The source produced no chunks. It may contain no readable text.")

        return ChunkPreviewResponse(
            document_id=document_id,
            source_characters=source_characters,
            chunks=shown,
            stats=ChunkPreviewStats(
                chunk_count=len(chunks),
                shown_chunk_count=len(shown),
                total_characters=sum(lengths),
                average_chunk_characters=round(sum(lengths) / len(lengths), 1),
                min_chunk_characters=min(lengths),
                max_chunk_characters=max(lengths),
                estimated_tokens=sum(max(1, length // 4) for length in lengths) if chunks else 0,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                strategy="FixedSizeChunkStrategy",
            ),
            warnings=warnings,
        )

    async def preview(self, request: ChunkPreviewRequest, user_id: str) -> ChunkPreviewResponse:
        text, document_id = await self._resolve_source(
            text=request.text, document_id=request.document_id, user_id=user_id
        )
        if not text.strip():
            raise BackendError(
                code="empty_source",
                message="The selected source contains no readable text.",
                status_code=422,
            )
        preview_document_id = document_id or f"preview-{uuid.uuid4().hex}"
        collection = self._chunk_text(
            text,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            document_id=preview_document_id,
        )
        return self._map_preview(
            collection,
            source_characters=len(text),
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            max_chunks=request.max_chunks,
            document_id=document_id,
        )

    async def compare(
        self, request: ChunkCompareRequest, user_id: str
    ) -> ChunkCompareResponse:
        text, document_id = await self._resolve_source(
            text=request.text, document_id=request.document_id, user_id=user_id
        )
        if not text.strip():
            raise BackendError(
                code="empty_source",
                message="The selected source contains no readable text.",
                status_code=422,
            )
        preview_document_id = document_id or f"preview-{uuid.uuid4().hex}"
        results = [
            self._compare_one(text, preview_document_id, config, request.max_chunks)
            for config in request.configs
        ]
        return ChunkCompareResponse(
            document_id=document_id,
            source_characters=len(text),
            results=results,
            warnings=[],
        )

    def _compare_one(
        self, text: str, document_id: str, config: ChunkConfig, max_chunks: int
    ) -> ChunkPreviewResponse:
        collection = self._chunk_text(
            text,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            document_id=document_id,
        )
        return self._map_preview(
            collection,
            source_characters=len(text),
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            max_chunks=max_chunks,
            document_id=document_id if not document_id.startswith("preview-") else None,
        )


def chunk_stats(chunks: list[Chunk]) -> dict[str, int]:
    """Small shared helper used by tests and the document inspector."""

    lengths = [len(chunk.text) for chunk in chunks]
    return {
        "count": len(lengths),
        "characters": sum(lengths),
        "min": min(lengths) if lengths else 0,
        "max": max(lengths) if lengths else 0,
    }
