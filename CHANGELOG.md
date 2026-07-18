# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Stage 12 - Learning Content Generation (Current)
- **Summary Generator**: First concrete Learning Generator transforming knowledge into pedagogical summaries.
- **OpenRouter Integration**: Fully decoupled `OpenRouterTextGenerationProvider`.
- **Validation**: Strict schema enforcement and placeholder rejection for LLM responses.
- **Metadata Flow**: Exhaustive generation tracking (`prompt_version`, `model_version`, etc.).

### Stage 11 - Pipeline Orchestration
- **Pipeline Domain**: Orchestration logic moving data unidirectionally across Bounded Contexts.
- **End-to-End**: A complete integration script demonstrating `Resource` -> `Summary` flow.

### Stage 10 - Knowledge Domain
- **Knowledge Graph**: Implemented immutable `KnowledgeConcept` and `KnowledgeRelationship`.
- **Knowledge Extraction**: AI-powered synthesis turning raw chunks into interconnected prerequisite graphs using Gemini and OpenRouter.

### Stage 9 - Retrieval
- **Search Capabilities**: Vector-based semantic search querying the Vector Store.
- **Ranking**: Strategies for ranking chunk relevance against queries.

### Stage 8 - Vector Store
- **Database Abstraction**: A provider-agnostic `VectorStore` interface.
- **ChromaDB**: Native integration for indexing `EmbeddingCollection`s.

### Stage 7 - Embedding Domain
- **Semantic Vectors**: Implementation of the `EmbeddingCollection` and `Embedding` data models.
- **Providers**: `AbstractEmbeddingProvider` and a concrete `LocalEmbeddingProvider` using `sentence-transformers`.

### Stage 6 - Hybrid Chunking
- **Hybrid Engine**: Developed `HybridChunkEngine` to orchestrate structural and fixed strategies based on document layout.
- **Fixed Strategy**: `FixedSizeChunkStrategy` as a robust fallback.

### Stage 5 - Structural Chunking
- **Chunk Models**: Immutable `Chunk` and `ChunkCollection` structures.
- **Structural Strategy**: `StructuralChunkStrategy` to split content intelligently at `HEADING` boundaries.

### Stage 4 - Advanced Content Processors
- **PDF Processor**: Layout-aware parsing of PDFs.
- **HTML Processor**: BeautifulSoup-powered extraction of web structures.
- **DOCX Processor**: Deep integration with Word document semantics.

### Stage 3 - Basic Content Processors
- **Processors**: `TXTProcessor` and `MarkdownProcessor`.
- **Normalization**: Translation of raw bytes into the unified `NormalizedDocument` structure.

### Stage 2 - Content Domain Foundations
- **Processor Registry**: Immutable plugin management.
- **Document Structure**: `Page`, `Block`, `Span` models preserving reading order and block atomicity.

### Stage 1 - Core Domain Foundations
- **Developer Experience**: A unified `uv` workspace structure supporting multiple pure Python packages.
- **Shared Domain**: Generic base entity classes (`Entity`, `ValueObject`, `DomainEvent`).
- **Learning Domain**: Core DAG validation (`PrerequisiteValidator`), `Subject`, `Concept`, and `LearningObjective` models.
- **Education Domain**: `Student`, `ProgressRecord`, `TutorSession`, and `Assessment` tracking models.
