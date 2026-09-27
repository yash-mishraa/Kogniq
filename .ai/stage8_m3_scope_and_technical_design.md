# Stage 8 M3 Scope and Technical Design: Reliability and Resiliency

## 1. Executive Summary
This document establishes the definitive scope and technical design for **Stage 8 M3 — Reliability and Resiliency**. It defines explicit resiliency boundaries around external dependencies (LLM providers, databases, and ingestion processes) and introduces targeted mechanisms—bounded retries, explicit timeouts, and state-machine recovery—to handle transient failures safely. The design rigorously preserves security isolation, idempotency mechanisms, and the existing architectural contracts established in previous milestones.

## 2. Authoritative Source Discovery
An audit of .ai/roadmap.md, .ai/system_blueprint.md, and the Kogniq repository established the following:
- **System Blueprint** dictates that pipelines must own retries and failure quarantine, and that failures/retries must be designed with the happy path.
- **Roadmap** describes Stage 8 as validating reliability and establishing SLOs.
- Existing code (packages/learning-content/src/learning_content/providers/gemini/provider.py) currently employs synchronous SDK calls (google.genai.Client) without native retries or backoff.
- Ingestion (packages/backend/src/backend/services/document_service.py) captures errors by transitioning DocumentJob to an "Error" state, but provides no native retry/recovery execution path.

## 3. Existing M3 Scope Definition
M3's scope is strictly bounded to implementing deterministic, observable resiliency primitives for known failure domains. It focuses on making failures explicit, testable, and recoverable without modifying the underlying domain logic, and without expanding into M4 (Prompt Hardening) or M5 (Load Testing/Release Gates).

## 4. Current Architecture / Dependency Map
- **LLM Provider (Gemini):** Invoked synchronously during TutorChatUseCase via provider.generate_chat. A failure here crashes the Tutor loop and propagates a 500 error.
- **Database / Unit of Work:** Managed asynchronously but wrapped in synchronous or asynchronous context managers (MemoryUowFactory / SQL implementations). Transaction boundaries are well-defined per use case.
- **Ingestion / Background Jobs:** DocumentService runs the ingestion pipeline and updates DocumentJob status in the DB. Failures remain terminal without retry mechanics.
- **Idempotency:** Learning interactions (Flashcards, Quizzes, Notebooks) already use robust server-derived idempotency_key semantics (e.g., "{session_id}_{tool_call.id}").

## 5. Current Reliability Gaps
1. **Provider Brittleness:** Transient 429s or 503s from the Gemini API crash the active TutorChatUseCase iteration.
2. **Stuck / Dead Ingestion Jobs:** If a worker crashes or a pipeline fails, DocumentJob is marked as "Error" (or left stuck in "Processing") with no recovery path.
3. **Missing Timeout Boundaries:** Synchronous LLM calls lack explicit API timeout bounds, risking unbounded latency and resource starvation.

## 6. Failure Taxonomy
- **Transient Failures (Retryable):** HTTP 429, 502, 503, 504 from the LLM provider. Temporary DB connection drops.
- **Permanent Failures (Non-Retryable):** Malformed prompts, 400 Bad Request, 401 Unauthorized, un-parseable LLM output, validation errors.
- **Timeouts:** Long-running pipeline operations or hanging LLM provider requests.
- **Process Failure:** Application crash during document ingestion.

## 7. Provider Resiliency Analysis
We must wrap the synchronous generate_content and generate_chat operations with a bounded retry policy. Because TutorChatUseCase orchestrates multiple tool steps, retrying the *entire* orchestrator loop is unsafe. Retries must occur strictly at the **provider adapter boundary** (inside gemini/provider.py) using bounded exponential backoff. 

## 8. Ingestion Recovery Analysis
DocumentJob needs a bounded recovery operation. Rather than building a heavyweight distributed queue, M3 will introduce a formal requeue/recovery method inside job_service.py or document_service.py that identifies stale/failed jobs and safely transitions them back to PENDING/Processing, resetting their pipeline states.

## 9. Database / Transaction Resiliency Analysis
Database commits via UnitOfWork generally fail safely (transactions roll back on exception). M3 will not introduce global DB retries because standard connection pooling handles minor transient network blips, and retrying arbitrary business logic risks violating state conditions. 

## 10. Idempotency Analysis
The current idempotency strategy utilizing idempotency_key = f"{session_id}_{tool_call.id}" correctly protects mutations. If the provider retries *internally* due to a 503, it will ultimately yield a single 	ool_call. If the orchestrator commits to DB and the DB succeeds but the API response fails, standard client retries safely hit the idempotent route. No new generalized idempotency framework is required.

## 11. Timeout Analysis
- **Provider Timeouts:** Hard timeouts (e.g., 30s) must be enforced at the generate_content boundary. 
- **Ingestion Timeouts:** Jobs stuck in Processing beyond a reasonable threshold (e.g., 30 minutes) should be detectable as "stale" and recoverable.

## 12. Recovery Semantics
- **Provider Transient:** Transparently retried with backoff. User sees slightly increased latency.
- **Provider Permanent/Exhausted:** Graceful exception thrown. Orchestrator halts. User receives a standard API error.
- **Ingestion Failure:** Job marked as "Error". A separate administrative or scheduled trigger can safely "requeue" the job.

## 13. M1 Telemetry Integration
M3 will emit structured M1 JSON logs for:
- provider_retry_attempt (fields: attempt_number, exception_class, delay_ms)
- provider_timeout (fields: elapsed_ms)
- ingestion_job_recovered (fields: job_id, previous_state)

## 14. M2 Evaluation Integration
M3 will add deterministic cases to packages/evaluation (e.g. eliability.yaml) that assert:
1. Provider transient failure followed by success yields correct orchestration.
2. Provider permanent failure safely aborts without infinite loops.

## 15. Security Analysis
Retries occur strictly *inside* the execution context of the currently authenticated user. Idempotency tags remain strictly scoped by session_id. Requeuing ingestion jobs must verify the tenant boundary. Security is fully preserved.

## 16. Proposed Architecture
- **Adapter Retry Wrapper:** 	enacity or custom bounded-async-retry logic injected into GeminiProvider.
- **Job Recovery Method:** DocumentService.recover_failed_jobs(user_id) to re-initiate failed document pipelines.
- **Timeout Decorator:** Enforce limits on synchronous LLM wrapper calls.

## 17. Detailed Retry Policies
- **LLM Provider:**
  - Max Attempts: 3
  - Backoff: Exponential (e.g., 1s, 2s, 4s)
  - Jitter: Yes
  - Retryable: Network errors, 429, 500, 502, 503, 504.
  - Non-retryable: 400, 401, 403.

## 18. Detailed Recovery Policies
- **Ingestion:** Provide an API or internal service method that finds DocumentJob rows where status == "Error", clears error_message, sets status = "Processing", and dispatches the background task again.

## 19. Test Strategy
- **Provider Retries:** Unit tests using unittest.mock.patch on genai.Client to simulate APIError(429) twice, followed by success. Verify it succeeds and telemetry is logged.
- **Ingestion Recovery:** Integration test proving a failed job can be re-run and artifacts are safely updated.
- **M2 Deterministic:** eliability.yaml evaluating the orchestrator against a failing provider stub.

## 20. M1/M2 Regression Plan
- Validate uv run pytest packages/evaluation/tests/ continues to pass.
- Verify logging formatting complies with M1 JSON specifications.
- Run the full 122+ backend test suite.

## 21. Release/SLO Signal Plan
Signals available for M5 release gates:
- Rate of provider_retry_attempt vs provider_success.
- provider_timeout frequency.
- Rate of DocumentJob entering Error state.

## 22. File-Level Change Plan
- packages/learning-content/src/learning_content/providers/gemini/provider.py (Add timeouts and retry logic).
- packages/backend/src/backend/services/document_service.py (Add ecover_job logic).
- packages/evaluation/datasets/tutor/reliability.yaml (New M2 dataset).
- packages/evaluation/tests/test_tutor_cases.py (Integrate reliability.yaml).
- pps/api/src/apps/api/app/routers/documents.py (Optional: expose recovery endpoint).

## 23. Explicit Non-Goals
- Global circuit breakers (deferred to M5 or infrastructure layer).
- Distributing the ingestion pipeline to Celery/Kafka.
- Prompt injection hardening (belongs to M4).
- Generalized workflow orchestration engine.

## 24. Risks and Trade-offs
- Synchronous provider SDK limits async scalability. We mitigate this by wrapping it in standard thread pool execution (or using async SDK methods if available in genai module, but current implementation relies on sync).
- Retry loops add latency, potentially frustrating users, so max attempts are strictly capped at 3.

## 25. Acceptance Criteria
| ID | Criterion | Status |
|---|---|---|
| AC-1 | Authoritative scope identified and dependency boundaries mapped. | VERIFIED NOW |
| AC-2 | Provider transient errors (429, 503) are retried at the adapter layer up to 3 times. | REQUIRES IMPLEMENTATION |
| AC-3 | Provider non-transient errors (400, 401) fail immediately. | REQUIRES IMPLEMENTATION |
| AC-4 | Provider calls enforce an explicit hard timeout. | REQUIRES IMPLEMENTATION |
| AC-5 | Ingestion service supports explicit recovery of 'Error' state jobs. | REQUIRES IMPLEMENTATION |
| AC-6 | Duplicate mutation risks analyzed; existing idempotency_key mechanism validated. | VERIFIED NOW |
| AC-7 | Telemetry emits provider_retry_attempt and provider_timeout events conforming to M1. | REQUIRES IMPLEMENTATION |
| AC-8 | M2 deterministic tests include reliability/provider-failure behaviors. | REQUIRES IMPLEMENTATION |
| AC-9 | Tenant isolation and security boundaries remain fully intact. | DESIGNED |
| AC-10 | Full M1/M2 regression suite executes with 0 violations. | DESIGNED |

## 26. Implementation Order
1. Update gemini/provider.py with retry/timeout logic and telemetry.
2. Update DocumentService with ecover_job functionality.
3. Write eliability.yaml and update 	est_tutor_cases.py.
4. Run regression suites and static analysis.

## 27. Final Verdict
READY FOR IMPLEMENTATION
