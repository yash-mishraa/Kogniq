# Retrieval API Architecture

The Kogniq Retrieval API exposes the underlying semantic search domain via a clean HTTP layer, strictly adhering to Dependency Inversion.

## Separation of Concerns

The fundamental architectural principle here is that the `RetrievalService` has no knowledge of semantic logic, embeddings, or Vector Store abstractions. It simply orchestrates the flow of data.

```mermaid
sequenceDiagram
    participant Client
    participant Router as RetrievalRouter
    participant Service as RetrievalService
    participant Retriever as SemanticRetriever
    participant VectorStore as ChromaVectorStore
    participant Repository as AbstractChunkRepository

    Client->>Router: POST /api/v1/retrieval/search (RetrievalRequest)
    Router->>Service: search(RetrievalRequest)
    
    Service->>Repository: get_by_document(document_id)
    Repository-->>Service: ChunkCollection (Hydration source)
    
    Service->>Retriever: retrieve(RetrievalQuery)
    Retriever->>VectorStore: search(query_embedding)
    VectorStore-->>Retriever: SearchResults
    Retriever-->>Service: tuple[RetrievalResult]
    
    Note over Service,Repository: Service matches chunk IDs from retrieval<br/>to actual Chunk objects.
    
    Service-->>Router: RetrievalResponse (safe metadata, no embeddings)
    Router-->>Client: 200 OK (JSON)
```

## Safety and Portability

1. **Hydration via Repository**: Semantic stores rarely guarantee absolute data integrity for text. The source of truth for text remains the `AbstractChunkRepository`.
2. **Abstract Boundaries**: `RetrievalFactory` supplies the concrete `LocalEmbeddingProvider` and `ChromaVectorStore` hidden behind `AbstractRetriever`.
3. **No Database Leakage**: Embeddings, vector distances, and internal database paths are never leaked into the `RetrievalResponse`.
