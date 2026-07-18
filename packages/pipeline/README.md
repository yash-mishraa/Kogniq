# Pipeline Package (`packages/pipeline`)

## Purpose
The `pipeline` package acts as the chief orchestrator of the Kogniq architecture. It is responsible for moving data unidirectionally across isolated bounded contexts (Content -> Embedding -> Retrieval -> Knowledge).

## Responsibilities

### What belongs here
- `DocumentIntelligencePipeline`: Orchestrates normalization, chunking, and graph extraction.
- End-to-End state management and logging.

### What does NOT belong here
- Direct file I/O or raw LLM interactions.
- Any domain-specific business rules.

## Public API
- `pipeline.intelligence.DocumentIntelligencePipeline`: Main entrypoint for processing a raw file into AI-ready vectors and knowledge graphs.

## Architecture
The pipeline is a pure orchestrator. It receives fully constructed concrete dependencies (Providers, Registries) via Dependency Injection and coordinates their execution sequentially.

## Dependencies
- `shared`
- `content`
- `embedding`
- `retrieval`
- `knowledge`

## Relationships
- Acts as the top-level integration layer prior to any Frontend or API boundary.

## Current Features
- End-to-end processing of a file into a `ChunkCollection`, indexing into a `VectorStore`, and extraction into a `KnowledgeGraph`.

## Planned Features
- Async pipeline execution for large-scale batch processing.
- Integration with the `LearningContent` bounded context.

## Examples
- `uv run python dev/demo_pipeline.py`

## Quality Gates
- **Tests**: `uv run python -m pytest packages/pipeline/tests/`
- **MyPy**: `uv run python -m mypy packages/pipeline/`
- **Ruff**: `uv run ruff check packages/pipeline/`
