import hashlib
from typing import Any

from content.chunking.collection import ChunkCollection
from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from content.domain.enums import ProcessingStatus, ResourceType
from content.normalized.document import NormalizedDocument
from content.pipeline.components.section import DefaultSectionExtractor


class LegacyIngestionAdapter:
    """Adapts legacy ingestion outputs to Content Intelligence models."""

    @staticmethod
    def map_document(doc: NormalizedDocument) -> LearningResource:
        return LearningResource(
            id=doc.id,
            title=doc.title,
            resource_type=ResourceType.TEXT,
            source=doc.source,
            checksum=doc.checksum,
            language=doc.language or "en",
            status=ProcessingStatus.PROCESSED,
        )

    @staticmethod
    def map_sections(resource: LearningResource, doc: NormalizedDocument) -> list[ResourceSection]:
        extractor = DefaultSectionExtractor()
        return extractor.extract_sections(resource, doc)

    @staticmethod
    def map_chunks(
        resource: LearningResource,
        sections: list[ResourceSection],
        collection: ChunkCollection,
    ) -> list[ResourceChunk]:
        if not sections:
            # Fallback section if extraction yielded nothing
            fallback_section = ResourceSection(
                id="default", resource_id=resource.id, title="Document Start", order=0
            )
            sections = [fallback_section]

        resource_chunks = []
        for i, old_chunk in enumerate(collection.chunks):
            section_id = sections[-1].id
            # Try to match the section based on legacy section_title
            if old_chunk.section_title:
                for section in sections:
                    if section.title.lower() in old_chunk.section_title.lower():
                        section_id = section.id
                        break

            # Checksum must not be empty
            text_bytes = old_chunk.text.encode("utf-8")
            checksum = hashlib.sha256(text_bytes).hexdigest()

            # Map legacy page numbers to chunk metadata
            meta: dict[str, Any] = {}
            if old_chunk.page_number is not None:
                meta["page_number"] = old_chunk.page_number
            if old_chunk.title:
                meta["title"] = old_chunk.title

            resource_chunks.append(
                ResourceChunk(
                    id=old_chunk.id,
                    resource_id=resource.id,
                    section_id=section_id,
                    text=old_chunk.text,
                    order=i,
                    checksum=checksum,
                    token_estimate=old_chunk.statistics.estimated_tokens,
                    metadata=meta,
                )
            )
        return resource_chunks
