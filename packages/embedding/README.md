# Embedding Domain (`kogniq-embedding`)

The `embedding` package is the canonical, provider-independent domain for representing vector embeddings in Kogniq.

## Purpose

To provide a pure, immutable data model for representing high-dimensional vectors extracted from textual chunks. It acts as the intermediary between the Chunk Engine and the downstream Retrieval layer.

## Responsibilities

- **Immutability**: Enforcing strict immutability for vectors and their metadata.
- **Validation**: Guaranteeing dimension consistency, non-emptiness, and provider homogeneity within collections.
- **Independence**: Operating entirely free of third-party APIs or heavy ML frameworks (no `torch`, `numpy`, `openai`, or vector DB SDKs).

## Future Providers

While the domain itself is provider-agnostic, future strategies will generate these vectors using:
- OpenAI (`text-embedding-3-small`, `text-embedding-3-large`)
- Google Gemini
- Ollama
- Sentence Transformers
