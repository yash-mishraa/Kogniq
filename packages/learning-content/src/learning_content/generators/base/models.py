from dataclasses import dataclass

from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection


@dataclass(frozen=True)
class GenerationContext:
    """
    Immutable context required for generation.
    Passes data across the PromptBuilder and Parser safely.
    """

    chunks: ChunkCollection
    graph: KnowledgeGraph


@dataclass(frozen=True)
class GenerationMetadata:
    """
    Lightweight metadata related to the text generation execution.
    Abstracts away the concrete provider instance from the Parser.
    """

    provider_name: str
    model_name: str
    model_version: str
    generation_version: str
    prompt_version: str
    generation_time_ms: float
