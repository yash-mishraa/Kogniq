from content.chunking.engine import HybridChunkEngine
from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from content.normalized.document import NormalizedDocument
from content.pipeline.interfaces import ChunkGenerator


class DefaultChunkGenerator(ChunkGenerator):
    """
    Generates chunks using the HybridChunkEngine, then adapts them to ResourceChunk.
    """

    def __init__(self) -> None:
        self.engine = HybridChunkEngine()

    def generate_chunks(
        self,
        resource: LearningResource,
        sections: list[ResourceSection],
        parsed_content: NormalizedDocument,
    ) -> list[ResourceChunk]:
        # Delegate chunking logic to the legacy engine
        chunk_collection = self.engine.chunk(parsed_content)

        resource_chunks = []
        for i, old_chunk in enumerate(chunk_collection.chunks):
            # Match chunk to section based on section title or page, simple fallback here
            section_id = sections[-1].id  # default to last section
            for section in sections:
                if section.title and old_chunk.section_title:
                    if section.title.lower() in old_chunk.section_title.lower():
                        section_id = section.id
                        break

            # Important: Create checksum for chunk
            import hashlib

            checksum = hashlib.sha256(old_chunk.text.encode()).hexdigest()

            r_chunk = ResourceChunk(
                resource_id=resource.id,
                section_id=section_id,
                text=old_chunk.text,
                order=i,
                checksum=checksum,
                token_estimate=old_chunk.statistics.estimated_tokens,
                metadata={
                    "page_number": old_chunk.page_number,
                    "title": old_chunk.title,
                },
            )
            resource_chunks.append(r_chunk)

        return resource_chunks
