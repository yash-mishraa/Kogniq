# Kogniq Architecture Packages

`packages/` contains the modular, bounded domain contexts and shared infrastructure libraries powering the Kogniq platform.

Each package adheres to Clean Architecture principles: business rules remain decoupled from frameworks, data storage, and external AI providers.

---

## Package Directory

| Package | Path | Purpose |
| :--- | :--- | :--- |
| **`shared`** | [`packages/shared`](shared/) | Foundation utilities: structured logging, environment loaders, and base exception hierarchies. |
| **`domain`** | [`packages/domain`](domain/) | Core domain models, value objects, domain events, and repository interfaces. |
| **`content`** | [`packages/content`](content/) | Content ingestion engine: PDF, Markdown, LaTeX, and plaintext processors with configurable chunking strategies. |
| **`embedding`** | [`packages/embedding`](embedding/) | Vector representations: provider-agnostic `AbstractEmbeddingProvider` implemented via HuggingFace `sentence-transformers` and Google Gemini. |
| **`retrieval`** | [`packages/retrieval`](retrieval/) | Hybrid retrieval engine: ChromaDB dense vector indexing fused with SQLite FTS5 BM25 search via Reciprocal Rank Fusion (RRF). |
| **`knowledge`** | [`packages/knowledge`](knowledge/) | Relational Knowledge Graph: conceptual ontology extraction, entity linking, and bounded BFS graph traversal. |
| **`learning`** | [`packages/learning`](learning/) | Pedagogical primitives: Flashcards (spaced repetition scheduling) and Quizzes (validated option scoring and explanation generators). |
| **`learning-content`** | [`packages/learning-content`](learning-content/) | Content synthesis: generative study guides, conceptual summaries, and structured learning units. |
| **`persistence`** | [`packages/persistence`](persistence/) | Data access layer: SQLite and in-memory Unit of Work (UoW) implementations, schema initialization, and transactional boundaries. |
| **`pipeline`** | [`packages/pipeline`](pipeline/) | Multi-stage document processing pipeline orchestrating parsing, chunking, embedding, and indexing. |
| **`jobs`** | [`packages/jobs`](jobs/) | Asynchronous job execution: durable SQLite-backed background task runner with recovery and state transitions. |
| **`evaluation`** | [`packages/evaluation`](evaluation/) | Benchmark harness: empirical evaluation of retrieval hit rate, MRR, grounded answer coverage, and token latency. |
| **`auth`** | [`packages/auth`](auth/) | Security & identity: Argon2 password hashing, HttpOnly session lifecycle, and role-based authorization (RBAC). |
| **`backend`** | [`packages/backend`](backend/) | Dependency injection container: singleton factories, provider routing, and application service integration. |
| **`application`** | [`packages/application`](application/) | Use-case orchestration: registration, hybrid retrieval, tutor interactions, and document management. |

---

## Architectural Rules

1. **Dependency Inversion**: High-level policies never depend on low-level details. All external stores (Chroma, SQLite, external LLMs) implement abstract interfaces.
2. **Boundary Isolation**: Packages never import from `apps/*`. Cross-package imports flow strictly inward toward core domains.
3. **Immutability & Type Safety**: Strict MyPy typing and Pydantic/dataclass schema contracts govern all inter-package communication.
