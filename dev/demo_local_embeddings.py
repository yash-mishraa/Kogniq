import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "embedding" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from embedding.providers import EmbeddingProviderRegistry
from embedding.providers.local.provider import LocalEmbeddingProvider

from content.chunking import Chunk, ChunkCollection


def main() -> None:
    print("Initializing Local Embedding Provider Registry...\n")
    
    registry = EmbeddingProviderRegistry()
    local_provider = LocalEmbeddingProvider()
    
    registry.register(local_provider)
    
    # Retrieve provider from registry
    provider = registry.provider("local")
    
    print("Loading model and obtaining metadata (this may take a moment)...")
    info = provider.info
    
    print("\n" + "-" * 40)
    print(f"Provider   : {info.provider_name}")
    print(f"Model      : {info.model_name}")
    print(f"Dimensions : {info.dimensions}")
    print("-" * 40)
    
    print("\nGenerating Embeddings...")
    
    from datetime import UTC, datetime

    from content.chunking import ChunkMetadata, ChunkStatistics
    
    def make_chunk(cid: str, text: str) -> Chunk:
        meta = ChunkMetadata(processor="demo", document_version="1", source="demo", checksum="1")
        stats = ChunkStatistics(
            character_count=len(text),
            line_count=1,
            word_count=len(text.split()),
            estimated_tokens=len(text.split()),
            processing_timestamp=datetime.now(UTC),
            confidence=1.0
        )
        return Chunk(
            id=cid, document_id="doc1", chunk_index=0, text=text,
            metadata=meta, statistics=stats, created_at=datetime.now(UTC)
        )
        
    chunk1 = make_chunk("c1", "The quick brown fox jumps over the lazy dog.")
    chunk2 = make_chunk("c2", "Artificial intelligence transforms modern computing.")
    chunk3 = make_chunk("c3", "Embedding models encode semantics into vector spaces.")
    
    collection = ChunkCollection(chunks=(chunk1, chunk2, chunk3))
    
    start = time.perf_counter()
    embs = provider.generate_batch(collection)
    end = time.perf_counter()
    
    print(f"\nGenerated {embs.total_embeddings} embeddings in {(end - start) * 1000.0:.2f} ms")
    
    first_emb = embs.embeddings[0]
    print(f"\nChunk ID       : {first_emb.chunk_id}")
    print(f"First 10 values: {first_emb.vector.values[:10]}")
    print(f"Vector Type    : {type(first_emb.vector.values).__name__}")
    
if __name__ == "__main__":
    main()
