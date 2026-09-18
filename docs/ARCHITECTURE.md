# System Architecture

Kogniq is designed as an agentic AI education system. Its architecture emphasizes robust data modeling, strict boundaries, and determinism.

## Architecture Principles

Our architecture is built on the following core principles:

- **Bounded Contexts**: The system is fractured into strict domain boundaries. Concepts in one domain do not leak into another.
- **Dependency Injection**: We use abstractions and inject concrete dependencies, ensuring testability and modularity.
- **Immutable Domain Models**: All domain models (e.g., `NormalizedDocument`, `ChunkCollection`, `KnowledgeGraph`) are deeply immutable. They are instantiated once and passed down the pipeline without side effects.
- **Provider-Agnostic Interfaces**: We never tightly couple to a specific AI vendor or database. Providers like Gemini, or ChromaDB are abstracted behind interfaces.
- **Registry Pattern**: We dynamically route tasks using registries (e.g., `ProcessorRegistry`, `GeneratorRegistry`).
- **Composition over Inheritance**: We favor small, composable functions and classes over deep inheritance hierarchies.
- **Infrastructure Isolation**: Core domain logic has no dependencies on external frameworks, databases, or AI APIs. The domain is pure.

## Workspace Dependency Diagram

The Kogniq monorepo is structured into a hierarchy of dependent workspaces:

```mermaid
flowchart TD
    shared --> content
    content --> embedding
    embedding --> retrieval
    retrieval --> pipeline
    content --> knowledge
    knowledge --> learning-content
    learning-content --> pipeline
    shared --> auth
    pipeline --> application
    auth --> application
    application --> apps_api[apps/api]
    apps_api --> apps_web[apps/web]
```

## Bounded Contexts

Kogniq currently implements the following bounded contexts:

### 1. Shared (`packages/shared`)
**Status: Implemented**
The foundational layer containing generic abstractions, interfaces, and utilities used universally across the codebase.

### 2. Content (`packages/content`)
**Status: Implemented**
Responsible for the physical structure of information. It ingests raw files, normalizes them, and builds Content Intelligence foundations (Resources, Sections, Chunks).

### 3. Chunking (Inside `content`)
**Status: Implemented**
Splits normalized documents deterministically via the `HybridChunkEngine` (combining `StructuralChunkStrategy` and `FixedSizeChunkStrategy`) into a `ChunkCollection`.

### 4. Embedding (`packages/embedding`)
**Status: Implemented**
Responsible for generating high-dimensional vectors from text using a provider-agnostic interface, producing an `EmbeddingCollection`.

### 5. Retrieval (`packages/retrieval`)
**Status: Implemented**
Handles indexing and searching embeddings using vector databases like ChromaDB and Qdrant.

### 6. Knowledge (`packages/knowledge`)
**Status: Implemented**
Synthesizes chunks into a structured `KnowledgeGraph` by extracting concepts and relationships using LLM providers.

### 7. Learning Content (`packages/learning-content`)
**Status: Implemented**
Generates educational artifacts like Summaries, Notes, Flashcards, Quizzes, and Study Guides utilizing chunk collections and knowledge graphs.

### 8. Pipeline (`packages/pipeline`)
**Status: Implemented**
Orchestrates the end-to-end execution flow, moving data sequentially across all bounded contexts.

### 9. Auth (`packages/auth`)
**Status: Implemented**
Manages user authentication, authorization, role-based access control (RBAC), and session management.

### 10. Application (`packages/application`)
**Status: Implemented**
Orchestrates user-facing use cases such as the Learning Loop, Playwright E2E integration, and analytics recording.

### 11. API (`apps/api`)
**Status: Implemented**
The FastAPI REST layer exposing domain pipelines, document jobs, and workspaces over HTTP.

### 12. Frontend (`apps/web`)
**Status: Implemented**
The React dashboard application powered by the immersive Workspace Engine.

## Current End-to-End Pipeline

This is the canonical workflow currently implemented in Kogniq:

```mermaid
flowchart TD
    RH[ResourceHandle]
    
    PR[ProcessorRegistry]
    ND[NormalizedDocument]
    HC[HybridChunkEngine]
    CC[ChunkCollection]
    EP[EmbeddingProvider]
    VS[(VectorStore)]
    KE[KnowledgeExtractor]
    KG[KnowledgeGraph]
    SG[SummaryGenerator]
    LC[LearningContent]

    RH --> PR
    PR --> ND
    ND --> HC
    HC --> CC
    CC --> EP
    EP --> VS
    CC -.-> KE
    KE --> KG
    CC -.-> SG
    KG -.-> SG
    SG --> LC
```
