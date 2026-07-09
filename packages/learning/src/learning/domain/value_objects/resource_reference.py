from dataclasses import dataclass
from enum import StrEnum


class ResourceType(StrEnum):
    VIDEO = "VIDEO"
    ARTICLE = "ARTICLE"
    INTERACTIVE = "INTERACTIVE"
    DOCUMENT = "DOCUMENT"


@dataclass(frozen=True)
class ResourceReference:
    """
    Points to the physical or logical location of a learning resource.
    """

    resource_type: ResourceType
    uri: str
    metadata: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.uri or not self.uri.strip():
            raise ValueError("Resource URI cannot be empty.")
