# Evaluation & Quality Gates

Kogniq enforces strict empirical evaluation for system reliability, performance, and security.

## RAG evaluation

The in-product Evaluation lab supports two modes:

- **Retrieval only** (`generate=false`): reports hit rate and MRR. Cases are
  marked `retrieval_only`; `answer_rate` and `grounded_rate` stay at `0` so a
  retrieval-only run cannot inflate answer quality.
- **Generated** (`generate=true`): runs the full grounded-answer path and adds
  answer rate, grounded rate, and citation coverage. Provider failures are
  recorded as `generation_failed` rather than reported as successful answers.

Metrics are persisted in `evaluation_runs` and surfaced through
`GET /api/v1/evaluation/history`.

## 1. Full Regression Suite

The system maintains a comprehensive `pytest` regression suite that must pass before any deployment.
- **Coverage:** Unit tests for all packages, bounded context integration tests, and application use-case end-to-end tests.
- **Current Baseline:** 492 collected, 492 passed (including RAG bootstrap,
  retrieval, chunking, evaluation, and ownership regression tests).

## 2. Deterministic Benchmark Infrastructure

To isolate application-side CPU overhead from LLM network non-determinism, Kogniq features a dedicated Benchmark environment.

- **`KOGNIQ_API_ENVIRONMENT=benchmark`**: Enables precise latency middleware.
- **`LEARNING_GENERATION_PROVIDER=deterministic-fake`**: Replaces the Gemini network call with a strict `asyncio.sleep` (default: 1000ms), allowing precise architectural benchmarking.

## 3. Release Gates

Kogniq's deployment pipeline is governed by explicitly defined gates:

### Hard Release Gates (Blocking)
1. **15% Latency Regression:** P95 latency for core application boundaries must not regress by >15% compared to the baseline (`1040.47 ms`).
2. **Tutor E2E (10-VU):** Concurrent stress of 10 virtual users must complete with a P95 `< 5000ms`. (Current Baseline: `~460 ms`).
3. **Notebook Lost-Updates:** 20 concurrent HTTP writes utilizing identical document contexts must persist with 0 lost updates, secured by idempotency keys.
4. **Tenant Isolation:** Vector retrieval strictly isolates chunk lookups by the requester's `user_id`. (0 leaks allowed).
5. **M4 Security Under Load:** Malicious prompt-injection instructions embedded in uploaded documents must not trigger unauthorized mutations.

### Stress/Observability Gates (WARN-only)
1. **Tutor E2E (100-VU):** Explores extreme event-loop queuing. This test warns if latency exceeds `5000ms`. 
    - *Note:* The default authoritative test server uses a single worker (`--workers 1`). Because the event-loop CPU overhead (FastAPI validation, SQLite parsing) for 100 concurrent requests requires ~4.3 seconds, this test natively warns (baseline `~5733 ms`). When deployed with multi-worker scaling (`--workers 4`), the architecture drops to `~2659 ms`. This gate is strictly an observability metric for single-worker limits, not a release blocker.
2. **SQLite Quantitative Lock Rate:** Warns if database locking errors exceed 0.1%. (Current baseline: `0.0%`).
