from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from content.domain.value_objects import ContentStatistics
from content.pipeline.interfaces import StatisticsExtractor


class DefaultStatisticsExtractor(StatisticsExtractor):
    """Computes basic statistics from sections and chunks."""

    def extract_statistics(
        self,
        resource: LearningResource,
        sections: list[ResourceSection],
        chunks: list[ResourceChunk],
    ) -> ContentStatistics:
        pages = set()
        for section in sections:
            if section.page_start is not None:
                pages.add(section.page_start)
            if section.page_end is not None:
                pages.add(section.page_end)
        for chunk in chunks:
            if chunk.metadata.get("page_number") is not None:
                pages.add(chunk.metadata["page_number"])

        # This is a very rough estimation, normally parser would provide true counts
        page_count = len(pages) if pages else 1

        return ContentStatistics(
            page_count=page_count,
            section_count=len(sections),
            chunk_count=len(chunks),
            image_count=0,
            table_count=0,
            formula_count=0,
        )
