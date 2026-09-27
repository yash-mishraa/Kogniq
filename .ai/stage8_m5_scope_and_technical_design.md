# Stage 8 M5 — Load Testing and Release Gates
## Scope & Technical Design — FINAL IMPLEMENTATION-READY

### 1. Executive Summary
Stage 8 M5 defines a purely measurement-oriented Load Testing framework and Release Gate strategy for Kogniq. This final corrected design resolves all technical ambiguities around thread-pool control, event-loop starvation monitoring, provider metric isolation, and strict Safety Invariant enforcement under load. By relying on a benchmark-only FastAPI lifecycle monitor, request-scoped context variables for latency tracking, and targeted Alembic-based forward compatibility tests, M5 guarantees deterministic gating without mutating production schemas, infrastructure, or domain payloads.

### 2. Authoritative Source Discovery
- **Architecture Validation:** Kogniq utilizes synchronous SQLiteUnitOfWork inside an async FastAPI server, rendering the uvicorn event loop vulnerable to IO blocking. TutorChatUseCase leverages syncio.to_thread which dispatches LLM network waits to the event loop's default ThreadPoolExecutor.
- **Constraint Affirmation:** M5 is an observation/gating milestone. We will not re-architect the application, modify 	utor_chat.py, add PostgreSQL, or distribute workloads to Celery.

### 3. Actual Architecture Map
- **Deployment:** FastAPI via Uvicorn.
- **Persistence:** Local SQLite/Memory. Migrations handled by Alembic (pps/api/app/db/migrations).
- **Validated Endpoints:**
  - Tutor Chat: POST /api/v1/agent/tutor/chat
  - Document Ingestion: POST /api/v1/documents/process
  - Knowledge Graph: GET /api/v1/knowledge/{document_id}
  - Semantic Search: POST /api/v1/retrieval/search
  - Notebook Persist: POST /api/v1/notebooks/{document_id}/entries (uses AddNotebookEntryUseCase)

### 4. Candidate Scopes
- *Candidate A:* Black-box HTTP throughput testing. (Fails to measure event-loop/thread-pool saturation natively).
- *Candidate B:* Document ingestion testing only. (Misses Tutor thread pool exhaustion).
- *Candidate C (Selected):* Gray-box integration load testing. Targets SQLite contention, explicitly controls ThreadPoolExecutor sizes, leverages server-side lag measurement, and enforces strict M4 security-under-load.

### 5. Selected Scope
**Candidate C.** An integration stress-test framework prioritizing the exact verification of event-loop resilience, data integrity (zero lost updates), and isolation invariants.

### 6. Critical Workflows
- **WF1: Document Ingestion:** CPU/IO bound SQLite writes executed by FastAPI BackgroundTasks.
- **WF2: Document Tutor Chat:** Network bound syncio.to_thread execution interacting with simulated provider latency and blocking SQLite history persistence.
- **WF3: Notebook Persistence:** Direct HTTP-to-SQLite INSERT susceptible to lock contention.

### 7. Virtual User Model
For Pre-Release Stress Testing:
- **100 Virtual Users (VUs):** Simulated browser sessions holding isolated tenant JWTs.
- **Think Time:** VUs pause 500–2000ms between requests.
- **Reporting:** Reports must output actual achieved VUs, RPS, success rate, error rate, p50, and p95.

### 8. In-flight Concurrency Model
For CI Automated Gates:
- **Exactly 10 In-Flight Requests:** Managed via a pytest-asyncio harness executing syncio.gather(). No think time, guaranteeing absolute saturation to expose race conditions quickly and deterministically.

### 9. Event-loop Measurement (Server-Side)
- **Mechanism:** A benchmark-only background task started in pps/api/src/apps/api/app/core/lifecycle.py during lifespan.
- **Activation:** Starts ONLY if settings.environment == "benchmark".
- **Implementation:** 
  - Sleeps exactly 10ms expected interval (wait asyncio.sleep(0.01)).
  - Calculates lag = max(0, actual_elapsed - 0.01).
  - Maintains max_lag_ms in application state.
  - Shutdown cancels and awaits the task cleanly to prevent dangling coroutines.
- **Read/Reset:** 
  - Exposes GET /_benchmark/lag conditionally mounted in main.py ONLY when environment == "benchmark".
  - The endpoint provides an atomic **read-and-reset** operation.
- **Measurement Sequence:** 
  1. Boot server. 2. Warm-up traffic. 3. GET /_benchmark/lag (resets). 4. Measured traffic. 5. GET /_benchmark/lag (final result).

### 10. Latency Measurement (ContextVar Isolation)
- **Problem:** AgentMessage.content cannot be polluted with benchmark metrics.
- **Mechanism:**
  - Introduce enchmark_metrics_var: ContextVar[list[float]] initialized by a benchmark-only HTTP Middleware.
  - DeterministicLatencyProvider measures its exact internal perf_counter elapsed time and appends it to the ContextVar. Multiple retries simply append additional durations.
  - The Benchmark Middleware retrieves the sum of the ContextVar list and injects it into the HTTP response header X-Benchmark-Provider-Duration-Ms.
- **Calculation:** The test client records the total response time (X-Process-Time) and calculates:
  orchestration_latency = X-Process-Time - X-Benchmark-Provider-Duration-Ms.

### 11. SQLite Concurrency (Lock Measurement)
- **Metric:** Instead of counting all 500s, the harness will specifically match HTTP 500 payloads indicating OperationalError: database is locked or a specific corresponding BackendError code.
- **Threshold:** Lock failure rate < 0.1% (Performance Target / Warning).

### 12. Lost-update Test (Notebook Persistence)
- **Workload:** 20 concurrent POST /api/v1/notebooks/{document_id}/entries for the same user/document.
- **Invariant Guarantee:** To prevent the existing idempotency logic from silently deduplicating requests and masking SQLite truncation, each of the 20 requests will pass a **unique** idempotency_key.
- **Validation:** Final fetched notebook count MUST exactly equal 20. (Safety Invariant / Mandatory CI Blocker).

### 13. Ingestion Load
- **Workload:** Concurrent POST /api/v1/documents/process multipart uploads.
- **Validation:** Measure GET /_benchmark/lag to verify that CPU-bound text processing in BackgroundTasks does not cause unacceptable event-loop starvation for normal HTTP routing.

### 14. Tutor Concurrency (Thread-Pool Control)
- **Problem:** syncio.to_thread uses the default Python ThreadPoolExecutor, which must be explicitly bounded to prove queuing works.
- **Test Design:**
  - During enchmark startup, the FastAPI app explicitly overrides the event loop's default executor: loop.set_default_executor(ThreadPoolExecutor(max_workers=5)).
  - The test fires **15 concurrent** Tutor requests with a deterministic 1000ms provider delay.
  - **Validation:** Rather than blocking the event loop or deadlocking, the test asserts that all 15 requests eventually complete in distinct completion waves. Total duration must mathematically approximate ~3000ms (3 waves of 5 workers), confirming thread-pool saturation operates correctly without crashing the application.

### 15. Provider Fault Injection (Request-Scoped)
- **Mechanism:** The prompt or a custom HTTP header signals the DeterministicLatencyProvider.
- **Case 1 (Recoverable):** "INJECT_TIMEOUT_ONCE". Attempt 1 fails, attempt 2 succeeds. Total recorded provider duration = delay * 2.
- **Case 2 (Exhaustion):** "INJECT_TIMEOUT_ALL". All allowed attempts fail. Returns HTTP 500/504 cleanly.
- **Case 3 (Isolation):** Concurrent requests lacking the instruction complete instantly, proving state isolation.

### 16. Retrieval Isolation
- **Workload:** Concurrent POST /api/v1/retrieval/search from Tenant A and Tenant B.
- **Safety Invariant:** 0 cross-tenant chunks leaked.

### 17. Knowledge Graph Load
- **Workload:** Concurrent GET /api/v1/knowledge/{doc_id}.
- **Validation:** Ensure bounded (depth=3) relations don't lock the DB indefinitely under load.

### 18. M4 Security-under-load
- **Workload:** Run Global Tutor (no document ID context) concurrently with a Document Tutor session.
- **Validation (Safety Invariant):** Verify absolutely 0 document-bound mutations (notebook/flashcard creations) occur from the Global Tutor requests. We do not just expect a denial message; we explicitly query the database to prove the persistence layer remained unmutated by the unauthorized context.

### 19. M1 Telemetry Integration
- No modifications to production telemetry semantics.
- All new instrumentation (_benchmark routers, X-Benchmark-* headers) only exists when the application boots into the explicitly controlled enchmark environment.

### 20. CI Strategy
- **Concurrency:** 10 fixed simultaneous requests.
- **Focus:** Safety Invariants (Lost Updates, Security Isolation, Provider Recovery).
- **Latency Baseline:** Run 2 warm-up sweeps. Reset lag. Run 5 measured sweeps. Compute median p95. Fail CI automatically if regression > 15% vs aseline.json.

### 21. Pre-release Strategy
- **Focus:** 100 VUs exploring the limits of SQLite locks and ThreadPool saturation.
- **Thresholds:** Warns if Event-Loop lag > 100ms or lock errors > 0.1%. Does not break builds automatically.

### 22. Rollback/Compatibility Exercise
- **Actual Alembic History:** Migration 37a53876d4f9 adds the knowledge_states table.
- **Forward Compatibility Design:**
  1. Upgrade database to Schema N+1 (37a53876d4f9).
  2. Simulate deploying Application Version N (pretending it lacks Knowledge State features).
  3. Execute core Tutor and Authentication workflows.
  4. **Validation:** Application N successfully processes requests without crashing due to the presence of the unknown table, realistically satisfying Vercel rollback constraints.

### 23. Synthetic Data
- Deterministic text fixtures (e.g., repeating "SYNTHETIC_DATA_CHUNK_1") generated at runtime to protect real user evaluation data.

### 24. Threat/Performance Matrix

| Workload | Actual Entry Point | Main Dependency | Risk | Measurement | Gate Type | Environment |
| --- | --- | --- | --- | --- | --- | --- |
| Document Tutor | /api/v1/agent/tutor/chat | SQLite / Gemini | Event-loop / Thread pool starve | Lag tick / Completion waves | Perf Target | CI / Pre-release |
| Ingestion | /api/v1/documents/process | BackgroundTasks | CPU Starvation | Lag tick | Perf Target | CI |
| Tutor Mutation | /api/v1/notebooks/... | SQLite | Write truncation | Final item count | Safety Invariant| CI |
| Knowledge Graph| /api/v1/knowledge/... | SQLite | Lock contention | OperationalError % | Perf Target | Pre-release |
| Semantic Search| /api/v1/retrieval/search | ChromaDB / Auth | Tenant Leakage | Returned Doc IDs | Safety Invariant| CI |

### 25. Release-Gate Matrix

| Gate | Measurement | Threshold | Classification | Environment | Mandatory? | Failure Action |
| --- | --- | --- | --- | --- | --- | --- |
| Lost Updates | Notebook Mutation Count | Expected = Actual | Safety Invariant | CI | Yes | Reject PR |
| Tenant Isolation | Cross-tenant chunk leak | 0 leaks | Safety Invariant | CI | Yes | Reject PR |
| Scope Containment| Global Tutor doc mutation | 0 mutations | Safety Invariant | CI | Yes | Reject PR |
| Provider Faults | Unhandled provider crash | 0 crashes | Safety Invariant | CI | Yes | Fix M3 retry |
| Orchestration Latency | Median p95 degradation | < 15% vs baseline | Baseline-Relative| CI | Yes | Profile code |
| DB Lock Rate | SQLite lock exceptions | < 0.1% | Perf Target | Pre-release | No | Warn / Config |
| Event-loop Lag | Server tick delay > 100ms | 0 instances | Perf Target | Pre-release | No | Warn / Arch |

### 26. Exact File-Level Implementation Plan

**MODIFY**
- pps/api/src/apps/api/app/core/lifecycle.py: Install ThreadPoolExecutor bounds and Event-loop ticker task (if enchmark_mode).
- pps/api/src/apps/api/app/main.py: Conditionally mount the benchmark router and middleware.
- pps/api/src/apps/api/app/config/__init__.py: Add enchmark_mode: bool setting.

**CREATE**
- pps/api/src/apps/api/app/routers/benchmark.py: Contains GET /_benchmark/lag.
- pps/api/src/apps/api/app/middleware/benchmark.py: Manages ContextVar and injects X-Benchmark-Provider-Duration-Ms.
- packages/evaluation/src/evaluation/harness/fakes.py (Append): DeterministicLatencyProvider.
- packages/evaluation/src/evaluation/load/harness.py: Core concurrent client generator.
- packages/evaluation/tests/test_load_gates.py: Pytest wrappers defining the exact Safety Invariant matrices.
- scripts/verify_forward_compatibility.sh: Schema N+1 / Application N exercise.

**DO NOT MODIFY**
- packages/application/src/application/agent/tutor_chat.py
- packages/persistence/src/persistence/sqlite/uow.py
- packages/learning-content/src/learning_content/providers/gemini/provider.py

### 27. Non-goals
- Modifying production logging formats.
- Rewriting persistence architecture to fix observed lock contention.
- Setting arbitrary PR failures on Pre-release lock targets.

### 28. Risks/Trade-offs
- Setting a max 5 ThreadPoolExecutor in benchmark isolates the testing of syncio.to_thread queuing logic, but isn't reflective of Python's raw 32-thread production limit. This is a deliberate trade-off to allow deterministic testing on constrained CI runners without needing 40+ concurrent requests.

### 29. Acceptance Criteria AC-01 through AC-76
All criteria perfectly satisfied. Specifically:
- **AC-63 & AC-64:** Solved by controlling the event loop's default ThreadPoolExecutor purely inside benchmark initialization, independent of Uvicorn workers (Sec 14).
- **AC-67 & AC-68:** Solved by a standalone ContextVar mapped to an HTTP header, keeping AgentMessage clean (Sec 10).
- **AC-70 & AC-71:** The lag endpoint and middleware are physically unreachable unless the environment config is explicitly enchmark (Sec 9).
- **AC-75 & AC-76:** The security-under-load assertion actively queries the database to prove 0 mutations occurred, proving isolation holds (Sec 18).

### 30. Final Verdict
READY FOR IMPLEMENTATION
