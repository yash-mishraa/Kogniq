from dataclasses import dataclass, field


@dataclass(frozen=True, kw_only=True)
class ResourceMetadata:
    """Immutable generic metadata associated with a resource."""

    attributes: dict[str, str] = field(default_factory=dict)
