import sys
from pathlib import Path

# Add the source directories to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "embedding" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "pipeline" / "src"))
# Add test directories to reuse fake implementations
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "pipeline" / "tests"))

from pipeline.pipeline import DocumentIntelligencePipeline
from test_pipeline import (  # type: ignore
    FakeChunkEngine,
    FakeEmbeddingProvider,
    FakeKnowledgeExtractor,
    FakeProcessor,
    FakeVectorStore,
)

from content.plugins.registry import ProcessorRegistry
from content.resource.handle import ResourceHandle


def main() -> None:
    print("=" * 80)
    print("Document Intelligence Pipeline Demo (Fake Dependencies)")
    print("=" * 80)

    # Construct the dependencies
    registry = ProcessorRegistry()
    registry.register(FakeProcessor())
    
    chunk_engine = FakeChunkEngine()
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()
    knowledge_extractor = FakeKnowledgeExtractor()

    # Construct the pipeline
    pipeline = DocumentIntelligencePipeline(
        processor_registry=registry,
        chunk_engine=chunk_engine,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        knowledge_extractor=knowledge_extractor,
    )

    from typing import cast
    from unittest.mock import MagicMock

    handle_mock = MagicMock(spec=ResourceHandle)
    handle_mock.id = "fake_doc_123"
    handle_mock.mime_type = "text/plain"
    handle_mock.extension = ".txt"
    
    print("\nExecuting pipeline.run()...\n")
    
    # Run the pipeline
    result = pipeline.run(cast(ResourceHandle, handle_mock))

    print("\n" + "=" * 80)
    print("Pipeline Execution Results")
    print("=" * 80)

    print(f"Total Execution Time : {result.metadata.total_processing_time_ms:.2f} ms")
    print(f"Document ID          : {result.content.document.id}")
    print(f"Pages Generated      : {len(result.content.document.pages)}")
    print(f"Chunks Generated     : {result.content.chunks.total_chunks}")
    print(f"Embeddings Generated : {len(result.embeddings.collection.embeddings)}")
    print(f"Embeddings Stored    : {result.embeddings.storage_result.stored_count}")
    print(f"Knowledge Concepts   : {result.knowledge.extraction_result.graph.concept_count}")
    print(f"Vector Store Count   : {vector_store.count()}")

    print("\nPipeline Architecture successfully orchestrated all components!")


if __name__ == "__main__":
    main()
