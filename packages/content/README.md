# Content Package (`packages/content`)

## Purpose
The `content` package is responsible for the physical structure and manipulation of raw information. It transforms unstructured files (PDF, HTML, TXT, etc.) into deterministic AI-ready chunks.

## Responsibilities

### What belongs here
- Ingesting raw bytes and streams via `ResourceHandle`.
- Extracting text, metadata, and document structure via `Processor`s.
- Modeling the canonical `NormalizedDocument` (Pages, Blocks, Spans).
- Chunking strategies (`StructuralChunkStrategy`, `FixedSizeChunkStrategy`).
- The `HybridChunkEngine`.

### What does NOT belong here
- LLM interaction or prompting.
- Embedding generation or semantic search.
- Knowledge graph extraction or educational concepts.

## Public API
- `content.processors.registry.ProcessorRegistry`: Routes files to correct parsers.
- `content.document.NormalizedDocument`: The immutable canonical structure.
- `content.chunking.HybridChunkEngine`: The entrypoint for splitting documents into chunks.
- `content.chunking.ChunkCollection`: The final output of the content pipeline.

## Architecture
Follows a strict ingest -> normalize -> chunk flow. Implements the Strategy Pattern for chunking and the Registry Pattern for processors.

## Dependencies
- `shared`

## Relationships
- Depended upon by: `embedding`, `knowledge`, `pipeline`.

## Current Features
- Robust processing of PDF, DOCX, Markdown, HTML, and TXT.
- Extensible `ProcessorRegistry`.
- Implemented `HybridChunkEngine` balancing semantic boundaries and token limits.

## Planned Features
- OCR support for scanned PDFs (via external multimodal provider integration).
- Table-specific structural chunking improvements.

## Examples
- `uv run python dev/demo_registry.py`
- `uv run python dev/demo_html_processor.py`
- `uv run python dev/demo_hybrid_chunk_engine.py`

## Quality Gates
- **Tests**: `uv run python -m pytest packages/content/tests/`
- **MyPy**: `uv run python -m mypy packages/content/`
- **Ruff**: `uv run ruff check packages/content/`
