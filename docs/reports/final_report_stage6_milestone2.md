# Final Report: Stage 6 Milestone 2 (Event Aggregation & Mastery Calculation)

## 1. Milestone 2 Objective
Transform governed analytics events from `learner_activity` into a deterministic, queryable `KnowledgeState` for a user and resource, keeping the aggregation algorithm modular and separate from existing API boundaries.

## 2. Supported Event Types
The baseline aggregation model categorizes events into:
- **Evidence-producing:**
  - `quiz_completed`
  - `flashcard_reviewed`
- **Activity/Progress only (ignored for mastery):**
  - `resource_viewed`
  - `chunk_viewed`
  - `study_session_completed`

## 3. Mastery Calculation Rules and Assumptions
- **Quiz Evidence:** Contributes `score / total_questions`.
- **Flashcard Evidence:** Maps string `difficulty` to a numerical value (`easy` -> 1.0, `good` -> 0.75, `hard` -> 0.25, `again` -> 0.0).
- **Aggregation:** A pure arithmetic average of all evidence scores for a given `(user_id, resource_id)`.
- **Bounds:** Values strictly clamped between 0.0 and 1.0.
- **Initial Score:** 0.0 if no valid evidence exists.
- **Timestamps:** `last_reviewed_at` is the maximum `occurred_at` (or `created_at`) from all events. `next_review_due` is a naive `last_reviewed_at + 1 day`.

## 4. Aggregation Architecture & Boundaries
The algorithm is isolated in `calculate_mastery` within `domain/student/mastery_calculator.py` as a pure function. Application-level integration is seamlessly injected into `RecordEventsBatchUseCase`, meaning that when the analytics worker flushes study events to the database, the affected `KnowledgeState` records are fully recomputed and upserted atomically in the same Unit of Work transaction.

## 5. Files Created or Modified
- `packages/domain/src/domain/student/mastery_calculator.py` (New: core algorithm)
- `packages/persistence/src/persistence/repositories/base.py` (Modified: Added `list_events_by_resource` to `AbstractAnalyticsRepository`)
- `packages/persistence/src/persistence/sqlite/analytics_repository.py` (Modified: Implemented SQL event fetching and mapping)
- `packages/persistence/src/persistence/memory/analytics_repo.py` (Modified: Memory filtering equivalent)
- `packages/application/src/application/analytics/record_events_batch.py` (Modified: Trigger domain recalculation immediately after event batch commits)
- `apps/api/tests/test_mastery_calculation.py` (New: algorithmic tests)

## 6. KnowledgeState Update Strategy
Updates are processed in batch. After `learner_activity` events are inserted by the background ingestion queue, the application fetches the complete historical event log for the affected `(user_id, resource_id)` pairs, recalculates the entire score deterministically, and overwrites the previous `KnowledgeState`.

## 7. Idempotency and Reprocessing Behavior
Because the algorithm is a pure function over the entire event history (a "left fold" of events into a score), it is natively idempotent and entirely insensitive to event ordering. Reprocessing the same event history repeatedly produces the exact same `KnowledgeState`. If events arrive out-of-order, the full recalculation simply slots them into their correct historical context.

## 8. API and Frontend Impact
- **API Impact:** None. The `KnowledgeState` read API remains unchanged.
- **Frontend Impact:** None. The frontend correctly consumes the read API and renders mastery seamlessly once the backend recalculates it. No observable structural changes were needed.

## 9. Tests Added & Results
Created `apps/api/tests/test_mastery_calculation.py` to independently verify algorithm behavior.
```text
uv run pytest apps/api/tests/test_mastery_calculation.py

======================== 4 passed, 1 warning in 0.06s =========================
```
Verified existing analytics and student backend tests passed alongside the new recalculation lifecycle:
```text
uv run pytest apps/api/tests/test_analytics.py apps/api/tests/test_student.py

======================== 23 passed, 1 warning in 5.73s ========================
```

## 10. Type-Checking and Linting Results
```text
uv run mypy .
Success: no issues found in 505 source files
```

## 11. Known Limitations
- The current mastery calculation is a simple average (mean) of all historical evidence. It does not account for time decay (forgetting curve) or varying difficulty weights beyond basic heuristics.
- `next_review_due` is naively hardcoded to 1 day after the last review.

## 12. Deferred Improvements
- Implement a sophisticated Spaced Repetition System (SRS) or Bayesian Knowledge Tracing model that weighs recent evidence more heavily than older evidence.
- Schedule asynchronous batch jobs to decrement `mastery_score` daily based on the Ebbinghaus forgetting curve.

## 13. Recommended Next Step
Proceed to **Stage 6 Milestone 3: Intelligent Spaced Repetition (Future)**, where the foundational arithmetic calculation can be safely replaced by a probabilistic retention algorithm without disrupting the existing pipeline boundaries.
