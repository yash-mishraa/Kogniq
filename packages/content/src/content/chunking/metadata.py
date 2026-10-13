from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class ChunkMetadata:
    """Metadata for a chunk, independent of processor and agnostic of AI engine specifics."""

    processor: str
    document_version: str
    source: str
    checksum: str
    language: str | None = None
    estimated_tokens: int | None = None
    estimated_characters: int | None = None
    section_id: str | None = None
    section_title: str | None = None
    section_path: str | None = None
    figure_id: str | None = None
    figure_number: str | None = None

    # Future placeholder properties (no implementation logic allowed)
    future_embedding_id: str | None = None
    future_graph_node_id: str | None = None
