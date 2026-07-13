# Retrieval Domain Foundation

**Last Updated:** 2026-07-13
**Status:** Implemented

## Context

The Retrieval Domain (Stage 9) introduces the orchestration layer that composes embedding generation and vector storage. It provides a pure, provider-agnostic semantic search interface (`AbstractRetriever`) for upstream consumers (e.g., Agents, RAG pipelines).

## Architectural Boundaries

Retrieval acts strictly as a translation and orchestration layer:

1. **Domain Input:** Receives a `RetrievalQuery`.
2. **Delegation:** 
   - Requests vector generation from an injected `AbstractEmbeddingProvider`.
   - Requests vector similarity search from an injected `AbstractVectorStore`.
3. **Domain Output:** Maps vector store `SearchResult` objects into clean `RetrievalResult` objects.

### Excluded Capabilities

To maintain clean module boundaries, the Retrieval Domain **does not**:
- Hydrate `Chunk` objects from a document database (deferred to a future Knowledge/Retrieval Repository).
- Re-rank results.
- Implement language models, prompt construction, or RAG orchestration.
- Couple to any specific ML or database framework (e.g., ChromaDB, OpenAI).

## Core Models

### `RetrievalQuery`
The immutable input model. Contains the exact text to search for, the desired limit (`top_k`), and optional metadata filters.

### `RetrievalResult`
The immutable output model. Intentionally extracts only the retrieval-specific context (e.g., `similarity_score`, `chunk_id`, `provider`, `model`) without exposing the underlying Vector Store primitives.

### `SemanticRetriever`
The canonical implementation of `AbstractRetriever`. Accepts `AbstractEmbeddingProvider` and `AbstractVectorStore` via dependency injection in its constructor.
