# Retrieval Package (`packages/retrieval`)

## Purpose
The `retrieval` package is responsible for indexing and searching vector embeddings. It bridges the gap between semantic vectors and the underlying chunk collections.

## Responsibilities

### What belongs here
- `AbstractVectorStore` interface for vector database interactions.
- Concrete implementations of vector stores (e.g., ChromaDB).
- Semantic search orchestration (`Retriever`).

### What does NOT belong here
- Vector generation (that belongs in `embedding`).
- Multi-agent orchestrations or RAG generation (that belongs in future packages).

## Public API
- `retrieval.store.base.AbstractVectorStore`: Interface for managing vector collections.
- `retrieval.store.registry.VectorStoreRegistry`: Dynamic resolution of stores.
- `retrieval.store.chroma.ChromaVectorStore`: Concrete implementation for ChromaDB.
- `retrieval.retriever.Retriever`: High-level search interface returning ranked chunks.

## Architecture
Provider-agnostic interface driven. The vector store implementations encapsulate all vendor-specific SDK calls.

## Dependencies
- `shared`
- `content`
- `embedding`

## Relationships
- Depended upon by: `pipeline` (in the future, RAG orchestration).

## Current Features
- Abstract `VectorStore` interface.
- Complete implementation of `ChromaVectorStore`.
- Basic Top-K retrieval mapping vectors back to underlying `Chunk` entities.

## Planned Features
- Hybrid Search (combining dense vectors with BM25 sparse search).
- Re-ranking algorithms.

## Examples
- `uv run python dev/demo_chroma_store.py`
- `uv run python dev/demo_retriever.py`

## Quality Gates
- **Tests**: `uv run python -m pytest packages/retrieval/tests/`
- **MyPy**: `uv run python -m mypy packages/retrieval/`
- **Ruff**: `uv run ruff check packages/retrieval/`
