# Kogniq Infrastructure & Deployment Architecture

This document details the production and staging infrastructure topology for the Kogniq system.

---

## Architecture Topology

```
                            ┌───────────────────────────────────────────────┐
                            │                 Vercel Edge                   │
                            │       Next.js 15 Frontend (apps/web)          │
                            │                                               │
                            │  - Global CDN & Static Assets                 │
                            │  - Client-side React State & KaTeX Rendering  │
                            │  - Reverse-Proxy: /api/:path* ────────────────┼───┐
                            └───────────────────────────────────────────────┘   │
                                                                                │ Same-Origin
                                                                                │ (Zero CORS)
                                                                                ▼
                            ┌───────────────────────────────────────────────┐
                            │      Backend Container (Render / VPS)         │
                            │             FastAPI (apps/api)                │
                            │                                               │
                            │  - Uvicorn Single-Worker ASGI Server          │
                            │  - Internal ThreadPoolExecutor (Concurrency)  │
                            │  - Local SentenceTransformers / Gemini Embed  │
                            │  - Hybrid Search Engine (Chroma + SQLite FTS) │
                            │  - Durable Background Job Queue               │
                            └───────┬───────────────────────────────┬───────┘
                                    │                               │
                                    ▼                               ▼
                     ┌─────────────────────────────┐ ┌─────────────────────────────┐
                     │    SQLite (WAL Mode)        │ │    ChromaDB (kogniq_v2)     │
                     │  - Users & Auth Credentials │ │  - 384-dimensional dense    │
                     │  - Document Index State     │ │    vector index (HNSW)      │
                     │  - Full-Text BM25 Chunks    │ │  - Page & Section metadata  │
                     │  - Query Telemetry Logs     │ │                             │
                     └─────────────────────────────┘ └─────────────────────────────┘
```

---

## 1. Container Configuration

The backend is packaged using a production-hardened `Dockerfile` based on `python:3.13-slim`:
- **Build tool**: Astral [`uv`](https://github.com/astral-sh/uv) for fast, deterministic, frozen dependency resolution.
- **Model Pre-caching**: The base embedding model (`all-MiniLM-L6-v2`) is pre-downloaded during container image construction, ensuring zero runtime download latency on cold boot.
- **Threading Limits**: Explicit environment boundaries (`TORCH_NUM_THREADS=1`, `OMP_NUM_THREADS=1`) prevent OpenMP thread over-subscription on virtual CPU cores.

---

## 2. Persistence & Storage

- **Relational Data**: SQLite in Write-Ahead Logging (`WAL`) mode with `busy_timeout=30.0` and foreign key enforcement enabled across all connections.
- **Vector Embeddings**: Persistent ChromaDB collection (`kogniq_v2`) storing chunk embeddings alongside exact page/section provenance.
- **File Uploads**: Incoming PDFs, LaTeX sources, and Markdown files are staged in `/app/data/uploads` with validated MIME types and unique UUID handles.

---

## 3. Observability & Health Probes

- **Liveness Probe**: `GET /api/v1/system/health` $\to$ Returns HTTP 200 when the Uvicorn ASGI server is responding.
- **Readiness Probe**: `GET /api/v1/system/overview` $\to$ Validates database connection, vector store availability, indexed document counts, and memory thresholds.
- **Query Telemetry**: Every search and generation turn records latency percentiles, token usage, groundedness status, and citation coverage in the `query_logs` store.

---

## 4. Production Operational Guidelines

- **Single-Worker Topology**: Due to SQLite single-writer concurrency design, the backend runs as a single Uvicorn worker process coupled with an internal asynchronous thread pool (default 50 workers) to eliminate multi-process lock contention.
- **Reverse Proxying**: Always terminate SSL/TLS at the edge (Cloudflare, Vercel, or Nginx/Caddy) and forward `Host` and `X-Forwarded-Proto` headers.
