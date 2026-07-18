# Embedding Package (`packages/embedding`)

## Purpose
The `embedding` package is responsible for translating raw text (specifically `Chunk`s) into high-dimensional semantic vectors using abstract, provider-agnostic interfaces.

## Responsibilities

### What belongs here
- Defining the `Embedding` and `EmbeddingCollection` domain models.
- Abstracting `AbstractEmbeddingProvider`.
- Concrete implementations of embedding providers (e.g., Local, OpenAI).

### What does NOT belong here
- Vector Database interactions (that belongs in `retrieval`).
- Text parsing or chunking logic (that belongs in `content`).

## Public API
- `embedding.models.EmbeddingCollection`: Immutable collection of generated vectors.
- `embedding.providers.base.AbstractEmbeddingProvider`: Interface for creating embeddings.
- `embedding.providers.registry.EmbeddingProviderRegistry`: Dynamic provider resolution.
- `embedding.providers.local.LocalEmbeddingProvider`: Concrete provider using `sentence-transformers`.

## Architecture
Provider-agnostic interface driven. The domain models are pure; external SDKs (like `sentence-transformers`) are encapsulated purely within concrete implementations and their adapters.

## Dependencies
- `shared`
- `content`

## Relationships
- Depended upon by: `retrieval`, `pipeline`.

## Current Features
- Fully typed immutable models for vectors.
- A functional `LocalEmbeddingProvider` using HuggingFace models.

## Planned Features
- `OpenAIEmbeddingProvider` implementation.
- `CohereEmbeddingProvider` implementation.

## Examples
- `uv run python dev/demo_embedding_domain.py`
- `uv run python dev/demo_local_embeddings.py`

## Quality Gates
- **Tests**: `uv run python -m pytest packages/embedding/tests/`
- **MyPy**: `uv run python -m mypy packages/embedding/`
- **Ruff**: `uv run ruff check packages/embedding/`
