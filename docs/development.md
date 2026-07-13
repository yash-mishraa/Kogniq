# Kogniq Development Guide

Welcome to the Kogniq development environment. This guide outlines the ergonomic workflow designed to ensure consistency across the repository.

## Workspace Overview

Kogniq relies heavily on `uv` to maintain a robust Python workspace spanning multiple sub-packages.
- `apps/`: Executable boundaries (e.g. `apps/api` for the backend).
- `packages/`: Agnostic, shared business and domain rules (`content`, `learning`, `education`). These are pure Python and isolated from frameworks.
- `dev/`: Developer demos and scripts that validate behaviors without needing a full UI.

## Environment Setup

1. Install [uv](https://github.com/astral-sh/uv).
2. Sync the workspace:
   ```bash
   uv sync
   ```

## Common Commands & Quality Gates

Code quality is enforced strictly by **Ruff**, **MyPy**, and **Pytest**. We expect `0` errors or warnings on any commit.

- **Run all tests**: `uv run python -m pytest`
- **Type Checking**: `uv run python -m mypy .`
- **Linting & Formatting**: `uv run ruff check .`
- **Auto-Fix Formatting**: `uv run ruff check . --fix`

## Developer Demos

To see Kogniq in action without booting up a web application, run the scripts in the `dev/` directory:

- `uv run python dev/demo_registry.py`: Demonstrates Processor Registry logic.
- `uv run python dev/demo_txt_processor.py`: Parses a mock `.txt` file into a `NormalizedDocument`.
- `uv run python dev/demo_markdown_processor.py`: Parses a mock `.md` file into a `NormalizedDocument`.
- `uv run python dev/demo_pdf_processor.py`: Parses a mock `.pdf` into a `NormalizedDocument`.
- `uv run python dev/demo_html_processor.py`: Parses a mock `.html` into a `NormalizedDocument`.
- `uv run python dev/demo_docx_processor.py`: Parses a mock `.docx` into a `NormalizedDocument`.
- `uv run python dev/demo_chunk_model.py`: Demonstrates the immutability of the base `Chunk` object.
- `uv run python dev/demo_structural_chunking.py`: Chunks a document based on `HEADING` blocks.
- `uv run python dev/demo_fixed_chunking.py`: Chunks a document strictly by character count.
- `uv run python dev/demo_hybrid_chunk_engine.py`: Orchestrates the decision between structural and fixed chunking dynamically.

## Adding Processors

To add support for a new file type (e.g., ePub):
1. Create a parser class extending `AbstractProcessor` in `packages/content/src/content/processors/epub_processor.py`.
2. Yield `NormalizedPage` and `NormalizedBlock` objects.
3. Register the processor in `packages/content/src/content/processors/registry.py`.
4. Create tests in `packages/content/tests/test_epub_processor.py`.
5. *Processors must not contain chunking logic!* Their only job is Normalization.

## Adding Chunk Strategies

To add a new chunking behavior (e.g., Semantic Chunking):
1. Create a strategy extending `AbstractChunkStrategy` in `packages/content/src/content/chunking/strategies/`.
2. It must accept a `NormalizedDocument` and return a `ChunkCollection`.
3. Do not mutate the original document.
4. Update `HybridChunkEngine` to incorporate the new strategy conditionally, or inject it manually where needed.

## Git Workflow & Release

1. Create a branch (`feature/xyz` or `fix/xyz`).
2. Run quality gates locally (`pytest`, `mypy`, `ruff`).
3. Create a Pull Request against `main`.
4. Ensure the CI pipeline passes.
5. Merge. Releases are automatically versioned using semantic versioning.
