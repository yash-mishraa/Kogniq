from content.domain.entities import LearningResource, ResourceSection
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.pipeline.interfaces import SectionExtractor


class DefaultSectionExtractor(SectionExtractor):
    """
    Extracts sections by finding heading blocks in the normalized document.
    """

    def extract_sections(
        self, resource: LearningResource, parsed_content: NormalizedDocument
    ) -> list[ResourceSection]:
        sections: list[ResourceSection] = []
        order = 0

        # A default section if document has no headings at start
        current_section = ResourceSection(
            resource_id=resource.id, title="Document Start", order=order, page_start=0
        )
        sections.append(current_section)

        for page in parsed_content.pages:
            for block in page.blocks:
                if block.block_type == BlockType.HEADING:
                    order += 1
                    current_section.page_end = page.page_number
                    current_section = ResourceSection(
                        resource_id=resource.id,
                        title=block.text.strip(),
                        order=order,
                        page_start=page.page_number,
                    )
                    sections.append(current_section)

        # Update end page for last section
        if parsed_content.pages:
            current_section.page_end = parsed_content.pages[-1].page_number

        return sections
