# Known Limitations

This document tracks genuine, confirmed limitations within the current Kogniq architecture.

## 1. SQLite Concurrency (Multi-Worker)
Kogniq utilizes SQLite in WAL (Write-Ahead Logging) mode. This provides excellent concurrency for a single event loop orchestrating writes via thread-pools. However, if deployed on a multi-worker server (e.g., `uvicorn --workers 4`), SQLite cross-process WAL synchronization introduces millisecond-level read staleness. A read request immediately following a write request on a different worker may observe an empty collection before the WAL is fully flushed.

## 2. Local Embedding Memory Characteristics
The `SentenceTransformers` implementation in the `embedding` package runs locally to maintain privacy and reduce cloud costs. This architecture is CPU/Memory intensive during document ingestion. Extreme ingestion loads (100+ concurrent large PDFs) will saturate the host CPU entirely.

## 3. Production Scaling and the 1,000-User Target
The current single-node deployment configuration has been empirically demonstrated up to 100 concurrent workers with zero errors. Supporting 1,000 concurrent users requires a distributed architecture:
- Horizontal API tier (multiple Uvicorn instances behind an NGINX / Cloudflare reverse proxy with load balancing).
- Externalized PostgreSQL database with PgBouncer connection pooling replacing single-writer SQLite.
- Externalized Qdrant vector database cluster replacing local ChromaDB.
- Distributed Redis token bucket replacing process-local rate limiting.

## 4. Single-Worker Event-Loop Starvation
Under extreme artificial concurrency (100+ synchronous Tutor requests), the single-threaded Python event loop introduces significant CPU-bound queuing (~43 ms per request), compounding total request latency linearly. This is mitigated in production by deploying with multi-worker ASGI servers.

## 5. No Prompt/KV Cache Reuse
Kogniq reports `cache_status: not_supported` for every query. Gemini's hosted
implicit caching is provider-controlled and exposes no portable KV-cache API
through this client, and local generation is not cached because answers depend
on the retrieved context. The telemetry does not claim a cache hit.

## 6. Retrieval Fusion Without Reranking
Hybrid retrieval fuses dense and BM25 candidates with reciprocal rank fusion.
There is no cross-encoder or LLM reranker, so near-duplicate chunks can occupy
several result slots. Scores are ranking signals, not calibrated probabilities.

## 7. Legacy Vector Collection
The original Chroma collection `kogniq` contains a corrupted HNSW index
(nearest-neighbour results disagreed with brute-force cosine similarity). New
writes use `kogniq_v2`; documents are only considered indexed after an explicit
reindex. The legacy collection is retained but never queried.

## 8. Semantic Enrichment Is Heuristic
Page and section metadata come from PDF layout and heading heuristics. Some
documents report a single section for many pages when headings are not
detectable. Semantic enrichment is not a substitute for a layout model.

## 9. Role Assignments Are Reconciled at Startup
Users and sessions are durable in SQLite, but role assignments live in the
process-local authorization provider. Startup grants the default `USER` role to
persisted accounts (and `ADMIN` to the development demo account) when no role
is present. Running multiple API workers would give each worker its own
authorization state; move roles into SQLite before horizontal scaling.

## 10. Durable Jobs (Single-Node Boundary)
`PersistentJobManager` persists background job metadata to the SQLite table `system_durable_jobs` and recovers interrupted `RUNNING` jobs on startup (`recover_stuck_jobs()`). However, the asynchronous worker queue (`asyncio.Queue`) is process-local. Multiple separate API processes cannot share or claim tasks from a shared pool without migrating to Redis Streams or a shared database claim lock.

## 11. Rate Limiting Scope
The sliding-window `RateLimitMiddleware` maintains timestamps in process memory. It provides strict protection for single-instance deployments, but across $N$ horizontally scaled instances behind a round-robin proxy, effective limits multiply by $N$. Production horizontal deployments must back the sliding window with Redis.
