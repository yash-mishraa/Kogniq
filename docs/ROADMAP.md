# Kogniq Roadmap

This document outlines the current state and future milestones for the Kogniq project.

## 🟢 Completed

The following bounded contexts, infrastructure elements, and capabilities are fully implemented in the Kogniq codebase:

- **Shared Infrastructure**: Base entities, exceptions, metadata models.
- **Content Processing**: Deterministic document normalization.
- **Processor Registry**: Pluggable architecture for parsing formats.
- **HTML Processor**: Advanced BeautifulSoup integration.
- **Universal Chunk Engine**: Core models for chunking.
- **Structural Chunking**: Semantic, layout-aware text splitting.
- **Fixed Size Chunking**: Deterministic fallback chunking by character limits.
- **Hybrid Chunk Engine**: Dynamic orchestration based on document structure.
- **Embedding Domain**: Immutable models for semantic vectors.
- **Embedding Providers**: Pluggable provider abstraction.
- **Local Embedding Provider**: Implementation using `sentence-transformers`.
- **Vector Store**: Provider-agnostic vector database abstraction.
- **ChromaDB**: Implementation of the Vector Store using `chromadb`.
- **Retrieval**: Search and ranking across vectorized chunks.
- **Knowledge Graph**: Domain modeling for Concepts and Relationships.
- **Knowledge Extraction**: AI-powered synthesis of text into knowledge graphs via OpenRouter and Gemini.
- **Pipeline**: End-to-end orchestration of content, embedding, and knowledge workflows.
- **Learning Content**: Core entities representing educational material.
- **Summary Generator**: Synthesis of knowledge into comprehensive summaries.
- **OpenRouter Provider**: Reference LLM provider integration.

## 🟡 Current

- **Learning Content Generation**: Completing the suite of specialized educational artifact generators using the established `AbstractLearningGenerator` pattern.

## 🔴 Upcoming

The following milestones are planned for future development:

- **Notes Generator**: Expanding generators to produce detailed study notes.
- **Flashcards**: Automated generation of spaced-repetition flashcards from chunks.
- **Quiz Generator**: Automated creation of multiple-choice and short-answer questions.
- **Study Guide Generator**: Synthesis of large knowledge graphs into structured syllabi.
- **API Layer**: Fastapi/REST endpoints exposing the core Kogniq pipelines.
- **Authentication**: User management and access control.
- **Frontend**: A React-based web dashboard for interacting with Kogniq.
- **Evaluation**: Quantitative metrics for measuring the quality of AI-generated content.
- **Deployment**: Dockerization and production infrastructure guides.
