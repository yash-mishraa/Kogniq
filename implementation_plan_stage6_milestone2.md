# Stage 6 Milestone 2: Event Aggregation & Mastery Calculation

## 1. Objective
Transform governed analytics events (from `learner_activity`) into a deterministic, queryable `KnowledgeState` for a user and resource, keeping the algorithm separate from the existing persistence and API boundaries.

## 2. Mastery Calculation Scope

### Event Contributions
- **Contribute to Mastery:**
  - `quiz_completed`: Provides objective evidence of understanding.
  - `flashcard_reviewed`: Provides self-reported evidence of recall.
- **Do Not Contribute to Mastery:**
  - `resource_viewed`, `chunk_viewed`, `study_session_completed`: These represent activity and progress, not verified mastery. They will not influence the `mastery_score`.

### Deterministic Baseline Rules
1. **Quiz Conversion:** A quiz event contributes an evidence score equal to `score / total_questions`. Invalid or 0-question quizzes are ignored.
2. **Flashcard Conversion:** A flashcard review contributes an evidence score based on the `difficulty` payload:
   - "easy" -> 1.0
   - "good" -> 0.75
   - "hard" -> 0.25
   - "again" -> 0.0
   - Unknown values are ignored.
3. **Repeated Events & Ordering:** All valid evidence scores for a given `(user_id, resource_id)` are simply averaged. This ensures the score is always strictly bounded between 0.0 and 1.0. Future milestones will introduce time-decay or Bayesian models.
4. **Initial Score:** If no valid evidence events exist, `mastery_score` evaluates to `0.0`.
5. **Timestamps:**
   - `last_reviewed_at`: The maximum `occurred_at` (or `created_at`) of the incorporated evidence events.
   - `next_review_due`: A simple deterministic placeholder: `last_reviewed_at + 1 day`. If no evidence exists, it is `None`.
6. **Incomplete Data:** Events missing required fields (e.g. `score`, `difficulty`) are ignored silently in the aggregation.
7. **Late-Arriving Events:** Handled perfectly by deterministic reprocessing. Since the algorithm just averages all historical evidence, event processing order does not matter.

## 3. Aggregation Boundary & Reprocessing Strategy

The existing ingestion flow (Analytics Queue -> `learner_activity` table via `AnalyticsRepository.save_events`) correctly deduplicates raw events.
We will **not** attempt to incrementally update `KnowledgeState` on every single web request, as that entangles ingestion with calculation.

Instead, we will create an Application Service: `CalculateKnowledgeStateUseCase`.
- **Input:** `user_id`, `resource_id`.
- **Logic:**
  1. Fetch all `learner_activity` events for the `(user_id, resource_id)`.
  2. Run the deterministic calculation loop in-memory.
  3. Upsert the resulting `KnowledgeState` using `AbstractKnowledgeStateRepository`.
- **Reprocessing:** Because the calculation is a pure function over the event history, it can be re-run at any time (e.g., synchronously requested by the frontend, or via an async worker) safely. It fully overwrites the previous state.

## 4. API & Frontend Impact

- The frontend currently renders the mastery score safely. No structural changes are needed.
- To wire the aggregation up: when a study session is completed (which drops events onto the queue), the frontend eventually needs the updated mastery. 
- *Option:* Since event delivery is async via a background queue, the KnowledgeState update could be triggered by the Analytics Worker after it flushes events.
- *Option:* We can expose a `POST /student/knowledge-states/{resource_id}/recalculate` endpoint, but to keep the frontend clean, we will wire the aggregation calculation directly into the Analytics worker or expose a domain event.
- *Decided Approach:* We will implement the core Aggregation logic as an independent Domain Service or Use Case. Then, we will wire it into the `FlushQueueUseCase` (which flushes analytics events) so that after events are persisted, the relevant `KnowledgeStates` are recalculated automatically.

## 5. Implementation Steps
1. **Domain Layer:** Implement `MasteryCalculator` pure function to process a list of `LearnerEvent`s into a `mastery_score` and `last_reviewed_at`.
2. **Application Layer:** Implement `RecalculateKnowledgeStateUseCase(user_id, resource_id)`.
3. **Integration:** Update `FlushQueueUseCase` to call `RecalculateKnowledgeStateUseCase` for every distinct `(user_id, resource_id)` pair present in the flushed batch.
4. **Testing:** Unit test `MasteryCalculator`, integration test `RecalculateKnowledgeStateUseCase`.
