# Kogniq Development Guide

Welcome to the Kogniq development environment. This guide outlines the ergonomic workflow designed to ensure consistency across the repository.

## Repository Structure

Kogniq uses a monorepo structure powered by `uv` workspaces.
- `apps/`: Future executable boundaries (e.g. `apps/api` for the backend).
- `packages/`: Agnostic, shared business and domain rules. These are pure Python and isolated from frameworks.
- `dev/`: Developer demos and scripts that validate behaviors end-to-end without needing a full UI.
- `docs/`: Architecture decisions, blueprints, and developer guides.

## Workspace Packages

- `shared`: Base abstractions and domain primitives.
- `content`: File processing, normalization, and structural chunking.
- `embedding`: Provider-agnostic vector generation.
- `retrieval`: Search and indexing against vector databases.
- `knowledge`: LLM-powered extraction of concepts and relationship graphs.
- `pipeline`: Orchestrators that route data across bounded contexts.
- `learning-content`: Generators that create educational artifacts.

## Environment Setup

1. Install [uv](https://github.com/astral-sh/uv).
2. Sync the workspace:
   ```bash
   uv sync
   ```

## Running Tests & Quality Gates

Code quality is enforced strictly by **Ruff**, **MyPy**, and **Pytest**. We expect `0` errors or warnings on any commit. Ensure you run these quality gates before submitting a Pull Request:

- **Run all tests**: `uv run python -m pytest`
- **Type Checking**: `uv run python -m mypy .`
- **Linting & Formatting**: `uv run ruff check .`
- **Auto-Fix Formatting**: `uv run ruff check --fix .` && `uv run ruff format .`

## Running Demos

To see Kogniq in action without booting up a web application, run the scripts in the `dev/` directory. They are grouped below by the pipeline stage they demonstrate:

### Content Processing
- `uv run python dev/demo_registry.py`: Demonstrates Processor Registry logic.
- `uv run python dev/demo_html_processor.py`: Parses a mock `.html` into a `NormalizedDocument`.

### Chunking
- `uv run python dev/demo_chunk_model.py`: Demonstrates the immutability of the base `Chunk` object.
- `uv run python dev/demo_structural_chunking.py`: Chunks a document based on `HEADING` blocks.
- `uv run python dev/demo_fixed_chunking.py`: Chunks a document strictly by character count.
- `uv run python dev/demo_hybrid_chunk_engine.py`: Orchestrates the decision between structural and fixed chunking dynamically.

### Embeddings
- `uv run python dev/demo_embedding_domain.py`: Demonstrates core embedding domain models.
- `uv run python dev/demo_embedding_registry.py`: Tests the dynamic registry of embedding providers.
- `uv run python dev/demo_local_embeddings.py`: Uses `sentence-transformers` to embed chunks locally.

### Vector Stores & Retrieval
- `uv run python dev/demo_vector_store_registry.py`: Tests the dynamic registry of vector stores.
- `uv run python dev/demo_chroma_store.py`: Interacts with ChromaDB to store and retrieve vectors.
- `uv run python dev/demo_retriever.py`: High-level semantic search across chunked collections.

### Knowledge Extraction
- `uv run python dev/demo_knowledge_registry.py`: Tests the dynamic registry of knowledge extractors.
- `uv run python dev/demo_openrouter_extractor.py`: Connects to OpenRouter (LLM) to extract a `KnowledgeGraph`.

### Learning Generation
- `uv run python dev/demo_learning_content.py`: Explores the raw `LearningContent` models.
- `uv run python dev/demo_openrouter_provider.py`: Directly tests the provider-agnostic LLM interface.
- `uv run python dev/demo_summary_generator.py`: Generates summaries using mock providers.
- `uv run python dev/demo_summary_openrouter.py`: Full AI generation of a summary using OpenRouter.

### Pipeline Orchestration
- `uv run python dev/demo_pipeline.py`: Runs a mock end-to-end pipeline covering normalization, chunking, and knowledge extraction.

## Git Workflow & Release

1. Create a branch (`feature/xyz` or `fix/xyz`).
2. Run quality gates locally (`pytest`, `mypy`, `ruff`).
3. Create a Pull Request against `main`.
4. Ensure the CI pipeline passes.
5. Merge.
