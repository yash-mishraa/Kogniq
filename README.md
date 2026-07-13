# Kogniq

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![uv](https://img.shields.io/badge/uv-fast-magenta.svg)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![MyPy](https://img.shields.io/badge/mypy-strict-success.svg)
![Pytest](https://img.shields.io/badge/pytest-passing-success.svg)
![License](https://img.shields.io/badge/license-MIT-green)

## Project Vision

Kogniq is an open-source, agentic AI educational platform designed to transform raw learning materials—such as textbooks, documentation, and research papers—into interactive, personalized tutoring experiences. 

## Why Kogniq exists

Most AI tutors are merely wrappers around chat models. They lack a deep understanding of the *structure* of learning materials and the *pedagogy* required to teach them. Kogniq solves this by building a rigorous, Domain-Driven Design (DDD) foundation that processes content semantically, builds prerequisite knowledge graphs, and utilizes multi-agent systems to tutor students effectively.

## Current Features

- **Robust Content Pipeline**: Ingests Markdown, PDF, DOCX, HTML, and TXT files.
- **Deterministic Normalization**: Converts diverse formats into a unified `NormalizedDocument` structure.
- **Hybrid Chunk Engine**: Dynamically orchestrates `StructuralChunkStrategy` and `FixedSizeChunkStrategy` to generate AI-ready `ChunkCollection`s without losing semantic boundaries.
- **Strict Bounded Contexts**: Pure Python implementations of Content, Learning, and Education domains.
- **100% Type Coverage**: Enforced by MyPy strict mode.

## Architecture Overview

Kogniq leverages a pure Python composition root with strict immutable data models.

```mermaid
flowchart TD
    A[ResourceHandle] --> B[ProcessorRegistry]
    B --> C[PDF / Markdown / DOCX / TXT / HTML Processors]
    C --> D[NormalizedDocument]
    D --> E[HybridChunkEngine]
    E --> F[StructuralChunkStrategy / FixedSizeChunkStrategy]
    F --> G[ChunkCollection]
    G --> H[(Future) Embeddings]
    H --> I[(Future) Retrieval]
    I --> J[(Future) Tutor]
```

*For more details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).*

## Monorepo Structure

We use `uv` workspaces to manage multiple independent Python packages in a single repository.

### Workspace Packages
- `packages/content/`: Responsible for file processing, normalization, and chunking.
- `packages/learning/`: Responsible for curriculum, concepts, and prerequisite knowledge graphs.
- `packages/education/`: Responsible for pedagogy, student modeling, and tutoring sessions.

## Technology Stack

- **Language**: Python 3.13
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Linting & Formatting**: Ruff
- **Type Checking**: MyPy
- **Testing**: Pytest

## Development Setup

1. Install `uv`:
   ```bash
   pip install uv
   ```
2. Sync the workspace:
   ```bash
   uv sync
   ```
3. Run the complete test suite:
   ```bash
   uv run python -m pytest
   ```

*See [docs/development.md](docs/development.md) for full instructions and developer demos.*

## Quality Gates

We enforce strict quality gates before any code is merged:
- All tests must pass (`uv run python -m pytest`).
- Code must be perfectly typed (`uv run python -m mypy .`).
- Code must be perfectly linted and formatted (`uv run ruff check .`).

## Current Status

We have completed the **Content Domain**, **Processors**, and the **Universal Chunk Engine**. The core foundational data models for Learning and Education are also implemented.

## Future Milestones

Please see [docs/ROADMAP.md](docs/ROADMAP.md) for a comprehensive view of upcoming features, including Semantic Chunking, Vector Embeddings, and the RAG infrastructure.

## Contributing

Contributions are welcome! Please read our [Development Guide](docs/development.md) to get started. Ensure all code passes the quality gates before submitting a pull request.

## License

MIT License. See `LICENSE` for details.
