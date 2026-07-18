# Knowledge Package (`packages/knowledge`)

## Purpose
The `knowledge` package bridges unstructured content with structured educational theory. It is responsible for modeling and extracting prerequisite graphs, concepts, and relationships from source texts.

## Responsibilities

### What belongs here
- Immutably modeling the `KnowledgeGraph`, `KnowledgeConcept`, and `KnowledgeRelationship`.
- AI-powered `KnowledgeExtractor` interfaces and implementations.

### What does NOT belong here
- Pedagogical artifacts like Flashcards or Quizzes (that belongs in `learning-content`).
- Chunk generation or physical file parsing (that belongs in `content`).

## Public API
- `knowledge.graph.KnowledgeGraph`: The immutable root entity connecting concepts and relationships.
- `knowledge.extractors.base.AbstractKnowledgeExtractor`: The provider-agnostic interface for LLM synthesis.
- `knowledge.extractors.registry.ExtractorRegistry`: Dynamic resolution of extraction providers.
- `knowledge.extractors.openrouter.OpenRouterExtractor`: Concrete implementation utilizing OpenRouter.

## Architecture
This package performs the critical "synthesis" step. It utilizes external LLMs strictly encapsulated behind the `AbstractKnowledgeExtractor` interface to ensure the domain model never leaks vendor specifics.

## Dependencies
- `shared`
- `content`

## Relationships
- Depended upon by: `learning-content`, `pipeline`.

## Current Features
- Full DAG enforcement for `KnowledgeGraph` relationships.
- Extraction via OpenRouter (e.g., Gemini and Llama 3 models).
- Immutable metadata tracking provenance down to the specific source chunk.

## Planned Features
- Multi-pass extraction strategies for extremely large documents.
- Continuous graph updating algorithms.

## Examples
- `uv run python dev/demo_knowledge_registry.py`
- `uv run python dev/demo_openrouter_extractor.py`

## Quality Gates
- **Tests**: `uv run python -m pytest packages/knowledge/tests/`
- **MyPy**: `uv run python -m mypy packages/knowledge/`
- **Ruff**: `uv run ruff check packages/knowledge/`
