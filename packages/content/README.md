# Content Domain (`kogniq-content`)

The `content` package is the bedrock of Kogniq's data ingestion pipeline. It is responsible for taking raw, unstructured files (PDFs, Markdown, DOCX, HTML, TXT) and transforming them into structured, AI-ready chunks.

## Responsibilities

- **Parsing**: Safely extracting text and structure from raw files.
- **Normalization**: Converting proprietary formats into a canonical, immutable `NormalizedDocument`.
- **Chunking**: Splitting documents into optimal sizes for embedding and retrieval without destroying semantic boundaries.
- **Orchestration**: Routing tasks via the `ProcessorRegistry` and `HybridChunkEngine`.

## What Belongs Inside

- File format parsers.
- Chunking algorithms (Fixed Size, Structural, Sliding Window).
- Immutable representations of documents, pages, blocks, and chunks.

## What Does NOT Belong Inside

- AI APIs (LLM calls, token generation).
- Vector databases or embedding generation.
- Pedagogical logic or curriculum graphs.

## Public API

The primary entry points for external consumers are:
- `ProcessorRegistry`: Register and retrieve processors for specific file types.
- `HybridChunkEngine`: The singular orchestrator for turning a `NormalizedDocument` into a `ChunkCollection`.
- `NormalizedDocument` & `ChunkCollection`: The immutable data structures yielded by the pipeline.

## Internal Architecture

The pipeline operates linearly:
`ResourceHandle` -> `ProcessorRegistry` -> `Concrete Processor` -> `NormalizedDocument` -> `HybridChunkEngine` -> `ChunkCollection`.

## Design Principles

- **Immutability**: All domain entities are frozen dataclasses.
- **Determinism**: Chunking the same document twice yields byte-for-byte identical results.
- **Composition**: Strategies are injected into engines, rather than using complex inheritance hierarchies.

## Current Status

**Implemented & Stable**. Processors for PDF, HTML, TXT, Markdown, and DOCX are complete. The Universal Chunk Engine (Structural and Fixed Size strategies) is complete.

## Future Work

- **Semantic Chunking**: A strategy that detects topical shifts.
- **Sliding Window Chunking**: A strategy that overlaps token boundaries.
