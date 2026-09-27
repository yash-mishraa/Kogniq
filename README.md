# Kogniq

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![uv](https://img.shields.io/badge/uv-fast-magenta.svg)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![MyPy](https://img.shields.io/badge/mypy-strict-success.svg)
![Pytest](https://img.shields.io/badge/pytest-passing-success.svg)
![License](https://img.shields.io/badge/license-MIT-green)

## Project Vision

Kogniq is an open-source, agentic AI educational platform designed to transform raw learning materials—such as textbooks, documentation, and research papers—into interactive, personalized tutoring experiences. 

Rather than acting as a generic chatbot wrapper, Kogniq is built upon a rigorous Domain-Driven Design (DDD) foundation. It processes content semantically, builds prerequisite knowledge graphs, enforces tenant isolation, and utilizes multi-agent systems to tutor students effectively.

## Repository Structure

Kogniq uses a modern monorepo structure powered by `uv` for the backend and `npm` for the frontend.

- `apps/api/` — The FastAPI backend.
- `apps/web/` — The Next.js/React frontend Workspace Engine.
- `packages/` — Isolated Python domain packages (e.g., `content`, `embedding`, `knowledge`, `application`).
- `docs/` — Architecture and developer setup documentation.

## Capabilities

Kogniq provides a complete, end-to-end foundation for AI educational content generation and tutoring:
- **Robust Ingestion**: Ingests Markdown, PDF, DOCX, HTML, and TXT files, converting them via a Hybrid Chunk Engine.
- **Provider-Agnostic Intelligence**: Local embeddings via SentenceTransformers; vector storage via Chroma/Qdrant; generation via Gemini.
- **Learning Content**: Automatically produces Summaries, Flashcards, Quizzes, and Study Guides from uploaded documents.
- **Agentic Tutor**: An autonomous, conversational Tutor Chat that uses semantic retrieval (RAG) to answer questions, explain concepts, and verify knowledge.
- **Immersive Workspace Engine**: A modern React frontend featuring split-pane Workspaces, Interactive Notebooks, a Knowledge Graph visualizer, and Flashcard/Quiz players.

## Local Setup & Development

See the definitive [Developer Setup Guide](docs/SETUP.md) for complete instructions on prerequisites, environment variables, SQLite initialization, and starting the development servers.

**Quick Start:**
```bash
# Clone the repository
git clone <repository_url>
cd Kogniq

# Sync Python packages
uv sync

# Run backend
uv run uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000

# Run frontend (in another terminal)
cd apps/web && npm install && npm run dev
```

## Testing & Quality

Kogniq enforces strict quality gates enforced by authoritative CI tests.

- **Full Regression**: `uv run pytest` (461 tests)
- **Static Analysis**: `uv run ruff check apps/ packages/`
- **Type Checking**: `uv run mypy apps/ packages/`

See [EVALUATION.md](docs/EVALUATION.md) for details on benchmark execution, security isolation verification, and load testing release gates.

## Documentation

Detailed documentation is available in the `docs/` directory:
- [Setup Guide](docs/SETUP.md) — Local installation, database setup, environment config.
- [Deployment Guide](docs/DEPLOYMENT.md) — Topology, environment, and server initialization.
- [Architecture](docs/ARCHITECTURE.md) — Detailed overview of Frontend, Backend, Agent, and Security architecture.
- [Evaluation & Gates](docs/EVALUATION.md) — Details the performance baselines, security tests, and stress benchmarks.
- [Known Limitations](docs/LIMITATIONS.md) — Current known technical and scaling boundaries.

## License

MIT License. See `LICENSE` for details.
