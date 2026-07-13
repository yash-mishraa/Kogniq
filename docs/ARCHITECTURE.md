# System Architecture

Kogniq is designed as an agentic AI education system. Its architecture emphasizes robust data modeling, strict boundaries, and determinism.

## Design Principles

Our architecture is built on the following core principles:

- **Domain-Driven Design (DDD)**: The system is fractured into strict Bounded Contexts. Concepts in the `Content` domain (like a parsed PDF chunk) do not leak into the `Learning` domain (like a prerequisite graph). 
- **Clean Architecture**: Core domain logic has no dependencies on external frameworks, databases, or AI APIs. The domain is pure.
- **Immutability**: All domain models (e.g., `NormalizedDocument`, `ChunkCollection`, `LearningResource`) are deeply immutable. They are instantiated once and passed down the pipeline without side effects.
- **Dependency Inversion**: High-level engines and orchestrators depend on abstract interfaces, not concrete implementations. For example, the `HybridChunkEngine` depends on `AbstractChunkStrategy`.

## Bounded Contexts

The monorepo is divided into several Python packages, each representing a bounded context:

### 1. Content Domain (`packages/content`)
**Status: Implemented**
Responsible for the physical structure of information. It ingests raw bytes (PDFs, Markdown, HTML), parses them using specialized `Processors`, normalizes them into a canonical `NormalizedDocument`, and splits them deterministically via the `HybridChunkEngine`.

### 2. Learning Domain (`packages/learning`)
**Status: Foundations Implemented**
Responsible for the curriculum and educational relationships. It models subjects, concepts, prerequisite graphs, and learning objectives. It does not know *what* the text of a PDF says, only *where* that PDF fits into a broader educational path.

### 3. Education Domain (`packages/education`)
**Status: Foundations Implemented**
Responsible for the pedagogy and interaction. This includes modeling the student (their progress, retention, and learning style) and the tutoring sessions (quizzes, explanations, feedback loops).

## Data Flow

Data flows unidirectionally through the system:

1. **Ingestion**: A user provides a file (e.g., a PDF textbook).
2. **Processing**: The `ProcessorRegistry` routes the file to the `PDFProcessor`, which extracts text, structure, and metadata, producing an immutable `NormalizedDocument`.
3. **Chunking**: The `HybridChunkEngine` evaluates the document's structure and delegates to the appropriate strategy (`StructuralChunkStrategy` or `FixedSizeChunkStrategy`), resulting in a `ChunkCollection`.
4. **Embedding (Future)**: Chunks are passed to an embedding model to generate semantic vectors.
5. **Retrieval (Future)**: The `Learning` domain constructs a knowledge graph. When a student asks a question, the `Education` domain performs Retrieval-Augmented Generation (RAG) against the vector database.
6. **Tutoring (Future)**: AI Agents leverage the retrieved context to tutor the student.

## Roadmap of Subsystems

- **Phase 1: Domain Foundations** (Completed) - Base entities, value objects, and pure logic for Content, Learning, and Education.
- **Phase 2: Content Pipeline** (Completed) - Processors, Normalization, and Chunking Engines.
- **Phase 3: AI & Embeddings** (Upcoming) - Integrating embedding models, vector databases, and semantic chunking.
- **Phase 4: Retrieval & RAG** (Planned) - Advanced context retrieval and graph traversals.
- **Phase 5: Agentic Tutors** (Planned) - Multi-agent orchestration for active tutoring and conversation.
- **Phase 6: Frontend & API** (Planned) - REST/GraphQL APIs and React UI.
