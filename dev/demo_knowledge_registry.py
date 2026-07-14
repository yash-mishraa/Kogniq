import sys
from pathlib import Path

# Add the source directories to sys.path so the demo can run without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from knowledge.extractors import (
    AbstractKnowledgeExtractor,
    KnowledgeExtractorInfo,
    KnowledgeExtractorRegistry,
)
from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection


class GeminiFakeExtractor(AbstractKnowledgeExtractor):
    @property
    def info(self) -> KnowledgeExtractorInfo:
        return KnowledgeExtractorInfo(
            extractor_id="gemini_pro",
            extractor_name="Gemini 1.5 Pro Extractor",
            version="1.5",
            provider="Google",
            supports_batch_processing=True,
            supports_streaming=True,
            maximum_chunks_per_request=100,
            maximum_tokens=2_000_000,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )

    def extract(self, chunks: ChunkCollection) -> KnowledgeGraph:  # noqa: ARG002
        return KnowledgeGraph(concepts=(), relationships=())

    def extract_batch(self, collections: tuple[ChunkCollection, ...]) -> tuple[KnowledgeGraph, ...]:
        return tuple(KnowledgeGraph(concepts=(), relationships=()) for _ in collections)


class LocalLLMFakeExtractor(AbstractKnowledgeExtractor):
    @property
    def info(self) -> KnowledgeExtractorInfo:
        return KnowledgeExtractorInfo(
            extractor_id="llama3_local",
            extractor_name="Llama 3 8B Local Extractor",
            version="3.0",
            provider="Meta",
            supports_batch_processing=False,
            supports_streaming=False,
            maximum_chunks_per_request=10,
            maximum_tokens=8192,
            supports_relationship_extraction=False,
            supports_alias_extraction=True,
        )

    def extract(self, chunks: ChunkCollection) -> KnowledgeGraph:  # noqa: ARG002
        return KnowledgeGraph(concepts=(), relationships=())

    def extract_batch(self, collections: tuple[ChunkCollection, ...]) -> tuple[KnowledgeGraph, ...]:
        return tuple(KnowledgeGraph(concepts=(), relationships=()) for _ in collections)


def main() -> None:
    print("Initializing Knowledge Extractor Registry Demo...\n")

    registry = KnowledgeExtractorRegistry()
    registry.register(GeminiFakeExtractor())
    registry.register(LocalLLMFakeExtractor())

    print(f"Total Extractors Registered: {registry.extractor_count}\n")

    print("Available Extractors:")
    for extractor_id in registry.available_extractors():
        ext = registry.extractor(extractor_id)
        info = ext.info
        print(f"  - [{info.extractor_id}] {info.extractor_name} v{info.version}")
        print(f"      Provider     : {info.provider}")
        print(f"      Max Chunks   : {info.maximum_chunks_per_request}")
        print(f"      Max Tokens   : {info.maximum_tokens:,}")
        print("      Capabilities :")
        print(f"        - Batch Processing: {info.supports_batch_processing}")
        print(f"        - Streaming       : {info.supports_streaming}")
        print(f"        - Relationships   : {info.supports_relationship_extraction}")
        print(f"        - Aliases         : {info.supports_alias_extraction}\n")

    print("--- Registry Built Successfully ---")


if __name__ == "__main__":
    main()
