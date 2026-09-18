from content.domain.entities import LearningResource
from content.domain.value_objects import ResourceMetadata
from content.normalized.document import NormalizedDocument
from content.pipeline.interfaces import MetadataExtractor


class DefaultMetadataExtractor(MetadataExtractor):
    """Extracts metadata from the NormalizedDocument."""

    def extract_metadata(
        self, resource: LearningResource, parsed_content: NormalizedDocument
    ) -> ResourceMetadata:
        # Fallback to resource language if parsed document does not have one
        language = resource.language
        author = None
        if parsed_content.metadata:
            author = parsed_content.metadata.author

        return ResourceMetadata(
            language=language,
            author=author,
            source_url=resource.source if resource.source.startswith("http") else None,
        )
