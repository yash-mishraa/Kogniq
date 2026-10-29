# Kogniq

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![uv](https://img.shields.io/badge/uv-fast-magenta.svg)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![MyPy](https://img.shields.io/badge/mypy-strict-success.svg)
![Pytest](https://img.shields.io/badge/pytest-passing-success.svg)
![License](https://img.shields.io/badge/license-MIT-green)

Kogniq is a RAG engineering console: upload documents, inspect how they were
chunked and embedded, compare chunking strategies, run hybrid retrieval,
get grounded answers with validated citations, evaluate retrieval quality, and
inspect real query telemetry.

The repository began as an educational tutor platform. The legacy study,
notebook, and knowledge-graph features still exist in the codebase, but the
primary product surface is now the RAG console described below.

## What actually works

| Area | Implementation |
| --- | --- |
| Ingestion | PDF, Markdown, and TXT via the registered content processors; stored uploads; authoritative per-document index state |
| Chunking | Fixed-size chunking with configurable size/overlap (`KOGNIQ_CHUNK_SIZE`, default `1200`; `KOGNIQ_CHUNK_OVERLAP`, default `200`), preview and side-by-side comparison |
| Embeddings | Local `SentenceTransformers` (`all-MiniLM-L6-v2`, 384 dimensions) |
| Vector store | Chroma, versioned collection `kogniq_v2` |
| Lexical search | SQLite FTS5 BM25 over persisted chunks |
| Retrieval | Hybrid vector + BM25 with reciprocal rank fusion (RRF), page/section provenance, per-document filtering |
| Generation | Provider-independent: Google Gemini (`gemini-2.5-flash`) primary with automatic fallback to local Ollama (`llama3.2:3b`), or pure local offline inference without API keys |
| Citations | Source IDs `[S1]`, `[S2]`, … validated against the retrieved set; invalid citations are reported and the answer is not marked grounded |
| Learning | Interactive Flashcards (3D flip, spaced repetition review) and Quizzes (4-choice validated scoring, explanations, mistake retake) |
| Knowledge Graph | Document concept extraction, relational node-link graph visualization, and bounded BFS subgraph traversal |
| Evaluation | Retrieval-only and generated-answer runs; hit rate, MRR, answer rate, grounded rate, citation coverage, latency |
| Observability | Persisted `query_logs` with retrieval/generation timings, token usage, citation validity, and cache status |
| Auth | SQLite-backed users and HttpOnly session cookies; ownership checks on every document and query |

## Architecture

```
Next.js RAG console (apps/web)
        │  same-origin /api/* rewrite
        ▼
FastAPI (apps/api)
        │
        ├── SQLite: users, sessions, documents, chunks, FTS5, query_logs, evaluation_runs
        └── Chroma: kogniq_v2 vectors
                │
                └── SentenceTransformers embeddings + Gemini generation
```

Retrieval is deliberately real: candidate vectors and BM25 hits are fused with
RRF. There is no cross-encoder reranker and no fake reranking stage. The prompt
treats retrieved text as untrusted data and instructs the model to ignore
instructions found inside documents.

## Local setup

Prerequisites: Python 3.13, [uv](https://github.com/astral-sh/uv), Node.js 20+,
and a Gemini API key for generated answers.

```bash
uv sync
cd apps/web && npm install && cd ../..
```

Create `.env` in the repository root:

```ini
KOGNIQ_API_ENVIRONMENT=development
PERSISTENCE_PROVIDER=sqlite
SQLITE_DATABASE_PATH=kogniq_dev.sqlite
GEMINI_API_KEY=your-key
```

Start the API and frontend:

```bash
uv run uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000
cd apps/web && npm run dev
```

In `development`, `test`, and `benchmark` environments the API seeds a demo
account:

- Email: `admin@kogniq.ai`
- Password: `password`

The frontend runs at `http://localhost:3000` and proxies `/api/*` to
`http://127.0.0.1:8000`.

## Everyday Workflows & Engineering Console

The user interface cleanly separates everyday learning capabilities from technical engineering inspection:

### Everyday Product Views
1. **Home** — System health, indexed document indicators, and quick action cards.
2. **My Documents** — Document library with authoritative indexing state, chunk counts, and reindex controls.
3. **Ask Questions** — Natural language search with grounded evidence citations `[S1]`, `[S2]`.
4. **Flashcards** — Interactive 3D flip card review, spaced confidence ratings (`Again`, `Hard`, `Good`, `Easy`), and manual card creation.
5. **Quizzes** — Multiple-choice assessment with instant radio scoring, explanations, mistake review, and retakes.
6. **Knowledge Graph** — Relational concept visualization with search filter, node inspector, and bounded BFS traversal.

### Engineering Console
- **Overview** — Document/index/query counts, embedding model, chunker config, provider diagnostics.
- **Chunking** — Side-by-side strategy comparisons and chunk distribution histograms.
- **Retrieval** — Dense vector vs lexical BM25 reciprocal rank fusion inspector.
- **Evaluation** — Suggested test cases, ground-truth hit rates, and citation coverage runs.
- **Activity** — Real query telemetry and latency percentiles.

## API surface

All routes are under `/api/v1` and require a session cookie except auth and health endpoints:

- `POST /auth/login`, `POST /auth/logout`, `POST /auth/register`, `GET /auth/session`
- `GET /system/overview`, `GET /system/ready`
- `GET /documents`, `POST /documents/process`, `GET /documents/{id}`, `GET /documents/{id}/chunks`, `POST /documents/{id}/retry`, `POST /documents/{id}/reindex`, `DELETE /documents/{id}`
- `POST /chunking/preview`, `POST /chunking/compare`
- `POST /rag/retrieve`, `POST /rag/query`
- `GET /learning/{document_id}`, `POST /learning/{document_id}/flashcards`, `POST /learning/{document_id}/quizzes`, `POST /learning/generate`
- `GET /knowledge/{document_id}`, `POST /knowledge/{document_id}/extract`, `GET /knowledge/{document_id}/query`
- `GET /evaluation/datasets`, `GET /evaluation/suggest`, `POST /evaluation/run`, `GET /evaluation/history`
- `GET /observability/queries`

## Verification

```bash
uv run pytest -q                 # 499 backend tests passed
cd apps/web
npx tsc --noEmit                 # TypeScript typecheck clean
npm run lint                     # ESLint 0 errors / 0 warnings
npm test -- --run                # 22 test files, 106 tests passed
npm run build                    # Next.js 15 production build succeeded
```

The E2E path used during recovery was: upload a PDF → wait for `Ready` →
reindex into `kogniq_v2` → run hybrid retrieval → ask a grounded question →
inspect citations and telemetry → run evaluation.

Full-tree `ruff check apps/ packages/` still reports legacy violations
(432 at the time of writing, down from 705 at the previous commit). No file
touched during this work has more Ruff findings than it had at `41ad6f1`, and
all newly added Python files are clean.

## Implemented vs. planned

Implemented: the ingestion, chunking, embedding, hybrid retrieval, grounded
generation, citation validation, evaluation, and telemetry paths listed above,
including persistent auth and ownership enforcement.

Opt-in / legacy: knowledge extraction and six-call learning generation are
disabled by default and enabled with `KOGNIQ_ENABLE_KNOWLEDGE_EXTRACTION` and
`KOGNIQ_ENABLE_LEARNING_GENERATION`. The legacy study, notebook, and
knowledge-graph screens remain reachable by URL but are not part of the RAG
console navigation.

Not implemented: DOCX/HTML ingestion (processors exist but are not registered),
cross-encoder reranking, streaming responses, OCR for scanned PDFs, multi-tenant
organizations, horizontal scaling of SQLite/Chroma, and provider KV-cache reuse
(reported as `cache_status: not_supported`). See
[docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Vercel Deployment Guide](docs/VERCEL_DEPLOYMENT_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Evaluation](docs/EVALUATION.md)
- [Known Limitations](docs/LIMITATIONS.md)
- [Deployment](docs/DEPLOYMENT.md)

## License

MIT License. See `LICENSE` for details.
