# Known Limitations

This document tracks genuine, confirmed limitations within the current Kogniq architecture.

## 1. SQLite Concurrency (Multi-Worker)
Kogniq utilizes SQLite in WAL (Write-Ahead Logging) mode. This provides excellent concurrency for a single event loop orchestrating writes via thread-pools. However, if deployed on a multi-worker server (e.g., `uvicorn --workers 4`), SQLite cross-process WAL synchronization introduces millisecond-level read staleness. A read request immediately following a write request on a different worker may observe an empty collection before the WAL is fully flushed.

## 2. Local Embedding Memory Characteristics
The `SentenceTransformers` implementation in the `embedding` package runs locally to maintain privacy and reduce cloud costs. This architecture is CPU/Memory intensive during document ingestion. Extreme ingestion loads (100+ concurrent large PDFs) will saturate the host CPU entirely.

## 3. Production Scaling
The default deployment configuration assumes a vertically scaled host (single large machine) rather than horizontally scaled containers, due to the local SQLite and local Vector database implementations.

## 4. Single-Worker Event-Loop Starvation
Under extreme artificial concurrency (100+ synchronous Tutor requests), the single-threaded Python event loop introduces significant CPU-bound queuing (~43 ms per request), compounding total request latency linearly. This is mitigated in production by deploying with multi-worker ASGI servers.
