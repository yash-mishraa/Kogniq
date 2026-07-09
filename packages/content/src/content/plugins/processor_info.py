from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class ProcessorInfo:
    """Immutable metadata about a content processor."""

    name: str
    version: str
    supported_extensions: tuple[str, ...]
    supported_mime_types: tuple[str, ...]
    description: str
