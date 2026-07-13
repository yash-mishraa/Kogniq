import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "embedding" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.providers import (
    AbstractEmbeddingProvider,
    EmbeddingProviderRegistry,
    ProviderInfo,
)

from content.chunking import Chunk, ChunkCollection


class MockProviderA(AbstractEmbeddingProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_id="mock_a",
            provider_name="Mock Provider A",
            model_name="mock-model-a",
            model_version="1",
            embedding_version="v1",
            dimensions=256,
            supports_batch_generation=True,
            supports_async_generation=True,
            maximum_batch_size=100,
            maximum_tokens=8192,
            normalized_output=True,
        )
        
    def generate(self, chunk: Chunk) -> Embedding:
        raise NotImplementedError
    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        raise NotImplementedError

class MockProviderB(AbstractEmbeddingProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_id="mock_b",
            provider_name="Mock Provider B",
            model_name="mock-model-b",
            model_version="2",
            embedding_version="v2",
            dimensions=1024,
            supports_batch_generation=False,
            supports_async_generation=False,
            maximum_batch_size=1,
            maximum_tokens=2048,
            normalized_output=False,
        )
        
    def generate(self, chunk: Chunk) -> Embedding:
        raise NotImplementedError
    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        raise NotImplementedError

def main() -> None:
    print("Building Embedding Provider Registry...\n")
    
    registry = EmbeddingProviderRegistry()
    
    provider_a = MockProviderA()
    provider_b = MockProviderB()
    
    registry.register(provider_a)
    registry.register(provider_b)
    
    print("-" * 32)
    print("Provider Registry Summary")
    print(f"Total Providers : {registry.provider_count()}")
    print("-" * 32)
    
    for provider in registry.available_providers():
        info = provider.info
        print(f"\nProvider Name : {info.provider_name} ({info.provider_id})")
        print(f"  Model       : {info.model_name} (v{info.model_version})")
        print(f"  Dimensions  : {info.dimensions}")
        print(f"  Batching    : {info.supports_batch_generation} (Max: {info.maximum_batch_size})")
        print(f"  Normalized  : {info.normalized_output}")

if __name__ == "__main__":
    main()
