# Kogniq Documentation

Comprehensive guides, architectural references, and deployment documentation for Kogniq.

---

## Core Guides

| Document | Description |
| :--- | :--- |
| **[Setup Guide](SETUP.md)** | Local development setup with `uv`, Node.js, and optional local LLM (`ollama`) or cloud Gemini. |
| **[Vercel & Production Deployment](VERCEL_DEPLOYMENT_GUIDE.md)** | End-to-end guide for deploying the Next.js frontend to Vercel and FastAPI to container hosts (Render, Railway, Fly). |
| **[Deployment Architecture](DEPLOYMENT.md)** | Single-node SQLite + Chroma topology, worker constraints, and reverse-proxy guidelines. |
| **[System Architecture](ARCHITECTURE.md)** | Package decomposition, Clean Architecture layers, data flow, and pipeline lifecycle. |
| **[Evaluation Suite](EVALUATION.md)** | Retrieval quality metrics (hit rate, MRR), citation coverage, and latency benchmark methodology. |
| **[Known Limitations](LIMITATIONS.md)** | Explicit technical constraints, concurrency boundaries, and deferred capabilities. |
| **[Roadmap](ROADMAP.md)** | Active milestones, completed capabilities, and future horizon. |
| **[Reports & Audits](reports/)** | Historical engineering milestones, verification reports, and acceptance audits. |

---

## Directory Overview

- **`architecture/`**: In-depth subsystem design documents (content processors, hybrid retrieval, vector indexing, evaluation harness).
- **`frontend/`**: Web UI patterns, design system token specifications, and workspace engine contracts.
- **`reports/`**: Complete historical audit, verification, and milestone closure reports.
