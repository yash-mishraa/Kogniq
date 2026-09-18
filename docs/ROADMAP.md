# Kogniq Roadmap

This document outlines the current state and future milestones for the Kogniq project.

## 🟢 Completed

The following bounded contexts, infrastructure elements, and capabilities are fully implemented in the Kogniq codebase:

- **Shared Infrastructure**: Base entities, exceptions, metadata models.
- **Content Processing**: Deterministic document normalization.
- **Processor Registry**: Pluggable architecture for parsing formats.
- **HTML, PDF, DOCX, TXT, Markdown Processors**: Advanced content integration.
- **Universal Chunk Engine**: Core models for chunking.
- **Structural, Fixed Size, and Hybrid Chunking**: Dynamic orchestration based on document structure.
- **Embedding Domain**: Immutable models for semantic vectors.
- **Embedding Providers & Vector Stores**: Local, Qdrant, ChromaDB integrations.
- **Retrieval**: Search and ranking across vectorized chunks.
- **Knowledge Graph & Extraction**: AI-powered synthesis of text into knowledge graphs via Gemini.
- **Pipeline Orchestration**: End-to-end orchestration of content workflows.
- **Learning Content Generators**: Complete suite including Summary, Notes, Flashcards, Quiz, Study Guide, and Explanation generators.
- **Core API Layer**: Fastapi/REST endpoints exposing pipelines, workspaces, and analytics.
- **Authentication & Authorization**: Multi-user isolation, memory and database providers.
- **Frontend Workspaces**: React-based interactive dashboards with Workspace Engine, Studio, and specialized views.
- **Intelligent Learning Loop**: End-to-end user experience with AI Tutor, "Explain my mistake", Analytics, and deterministic next-action recommendations.
- **Content Intelligence Foundation**: Framework-independent Domain models for Learning Resources, Sections, and Chunks.
- **Content Intelligence Persistence**: Incremental integration adapters and SQLite persistence with full ownership isolation.

## 🟡 Current

- **Content Intelligence Expansion**: Enhancing the intelligence models to completely replace legacy chunks across all downstream consumers.
- **Deployment & Infrastructure**: Refining Dockerization, production guides, and CI/CD.

## 🔴 Upcoming

The following milestones are planned for future development:

- **Multi-Agent Systems**: Introducing complex tutoring behaviors through collaborative AI subagents.
- **Advanced Evaluation**: Expanding quantitative metrics for measuring the pedagogical quality of AI-generated content.
- **Spaced Repetition Engine**: Integrating flashcards with an algorithmic SRS scheduling backend.
- **Social Learning**: Enabling shared workspaces and peer-to-peer knowledge graph collaboration.
