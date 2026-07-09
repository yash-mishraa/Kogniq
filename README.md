# Kogniq

An open-source AI Learning Intelligence Platform designed to elevate domain-specific knowledge acquisition through Retrieval-Augmented Generation (RAG), Knowledge Graphs, and intelligent recommendation systems.

*Note: This is a robust AI orchestration backend for learning domains. It is NOT just a chatbot.*

---

## 🎯 Vision
Kogniq aims to transition standard educational experiences into intelligent, data-driven platforms. By understanding both the structure of the domain (Knowledge Graphs) and the student's mastery profile (Student Modeling), it creates highly effective adaptive learning pathways.

## 🏗 Architecture Overview
The platform enforces a strict separation of concerns utilizing Clean Architecture principles:
- **Domain-Driven Design:** Business rules are entirely decoupled from frameworks.
- **RAG & Agentic AI:** Integrates language models for contextual learning, validated generation, and deep semantic search.
- **Modular Monorepo:** Python `uv`-based workspace scaling across APIs, Shared Core, and Domain Plugins.

## 🛠 Tech Stack
- **Language:** Python 3.12+ (Strictly Typed)
- **API Framework:** FastAPI with Uvicorn
- **Persistence:** PostgreSQL with SQLAlchemy 2.x and asyncpg
- **Migrations:** Alembic
- **Caching/Queues:** Redis (Planned)
- **Dependency Management:** `uv`
- **Linting & Quality:** Ruff, MyPy, Pytest

## 📂 Repository Structure
```text
Kogniq/
├── apps/               # Executable applications (e.g., API)
├── packages/           # Internal shared libraries (e.g., core domain logic)
├── docs/               # Technical and developer documentation
├── scripts/            # Advanced non-interactive operational utilities
├── tests/              # E2E integration tests (module tests live inside apps/packages)
└── docker-compose.yml  # Local infrastructure orchestration
```

## 🚀 Quick Start

### 1. Installation
1. Install [uv](https://github.com/astral-sh/uv).
2. Install [Docker](https://docs.docker.com/get-docker/).
3. Clone the repository:
   ```bash
   git clone https://github.com/yash-mishraa/Kogniq.git
   cd Kogniq
   ```
4. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
5. Install dependencies and setup the virtual environment:
   ```bash
   make setup
   ```

### 2. Local Infrastructure (Docker)
Start the PostgreSQL and Redis containers:
```bash
make docker-up
```

*Ensure the database is healthy:*
```bash
make docker-status
```

### 3. Database Migrations
Initialize your database schema:
```bash
make db-upgrade
```

### 4. Running Locally
Start the local FastAPI development server:
```bash
make dev
```
The API will be accessible at `http://127.0.0.1:8000`.

## 🧪 Quality Commands
Ensure your code meets the quality standards before committing:
- **Format & Lint:** `make format` & `make lint`
- **Type Checking:** `make typecheck`
- **Testing:** `make test`
- **Run Everything:** `make quality`

## 📘 Development Workflow
For deeper insights on repository ergonomics, backend architecture, and troubleshooting, please read our [Development Guide](docs/development.md).

## 🗺 Roadmap
- [x] Foundation & Monorepo Setup
- [x] Database Persistence & Clean Architecture
- [ ] Authentication & User Identity Management
- [ ] Knowledge Graph Integration & RAG Engine
- [ ] Adaptive Student Modeling & Agentic Plugins
- [ ] Production-Ready Deployment configuration

## 🤝 Contributing
Contributions are welcome! Please review our quality guidelines in `docs/development.md` and ensure all PRs pass `make quality` before submitting.

## 📄 License
This project is proprietary while in early development. An open-source license will be established prior to public release.
