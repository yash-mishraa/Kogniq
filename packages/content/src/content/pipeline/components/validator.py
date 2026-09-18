from content.domain.entities import LearningResource
from content.pipeline.interfaces import ContentValidator


class DefaultContentValidator(ContentValidator):
    """Validates that a LearningResource has basic required properties."""

    def validate(self, resource: LearningResource) -> tuple[bool, str]:
        if not resource.title or not resource.title.strip():
            return False, "Resource title cannot be empty."
        if not resource.source or not resource.source.strip():
            return False, "Resource source cannot be empty."
        if not resource.checksum or not resource.checksum.strip():
            return False, "Resource checksum cannot be empty."
        return True, "Valid resource."
