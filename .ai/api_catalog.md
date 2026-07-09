# Planned API Catalog

This is an inventory of possible external application APIs, not an implementation or finalized contract. Paths, methods, schemas, versioning, authentication, and grouping require later design review. Every entry has status **Not Implemented**. Internal package interfaces are defined separately in [`package_contracts.md`](package_contracts.md).

## API Rules

- `apps/api` will be the authority for externally exposed product workflows.
- Authentication does not imply authorization; every protected operation requires an explicit policy.
- Inputs and outputs refer to conceptual objects in [`data_dictionary.md`](data_dictionary.md), not wire schemas.
- Collection APIs require bounded pagination and filtering.
- Creation and long-running operations require idempotency and status semantics where applicable.
- Errors must be structured, safe, correlated, and documented.
- Breaking contracts require ADR, migration notes, compatibility policy, and progress update.

## System and Domain APIs

| Future API | Purpose | HTTP Method | Authentication Requirement | Expected Inputs | Expected Outputs | Dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/health` | Report process liveness without dependency details | `GET` | None; network policy still applies | None | Minimal liveness status | Configuration, Logging | Not Implemented |
| `/ready` | Report whether the application can safely receive traffic | `GET` | Operator/network restricted | None | Readiness and non-sensitive dependency status | Configuration, Logging | Not Implemented |
| `/v1/domains` | List installed, enabled, compatible learning domains | `GET` | Optional for public metadata; policy undecided | Pagination, locale | Domain summaries and compatibility metadata | Configuration, domain registry | Not Implemented |
| `/v1/domains/{domain_id}` | Inspect one available domain and curriculum options | `GET` | Optional; policy undecided | Domain identifier, locale | Domain metadata, supported curriculum versions | Domain registry, Knowledge Graph | Not Implemented |
| `/v1/domains/{domain_id}/curriculum` | Navigate a versioned domain curriculum | `GET` | Required for learner-specific annotations; otherwise policy undecided | Domain, curriculum version, filters | Topics, Concepts, relationship summaries | Knowledge Graph | Not Implemented |

## Identity and User APIs

| Future API | Purpose | HTTP Method | Authentication Requirement | Expected Inputs | Expected Outputs | Dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/v1/auth/sign-in` | Establish an authenticated session | `POST` | Pre-authentication controls | Approved credential/assertion, client context | Session result or safe failure | Authentication, Configuration, Logging/audit | Not Implemented |
| `/v1/auth/sign-out` | End the current session | `POST` | Required | Session context | Revocation outcome | Authentication, Logging/audit | Not Implemented |
| `/v1/auth/session` | Inspect current session assurance and expiry | `GET` | Required | Session context | Principal/session metadata | Authentication | Not Implemented |
| `/v1/users/me` | Read or update the user's eligible profile/preferences | `GET`, `PATCH` | Required; self or privileged policy | Field mask or validated preference changes | User profile/preferences and version | Authentication, user owner, Configuration | Not Implemented |
| `/v1/users/me/export` | Request an export of eligible personal data | `POST` | Required with elevated verification | Export scope and format preference | Accepted job, status reference | Authentication, privacy workflow, service owners | Not Implemented |
| `/v1/users/me/deletion` | Request deletion of eligible personal data | `POST` | Required with elevated verification | Scope, confirmation, legal context | Accepted request and limitations/status | Authentication, privacy workflow, service owners | Not Implemented |

## Document and Retrieval APIs

| Future API | Purpose | HTTP Method | Authentication Requirement | Expected Inputs | Expected Outputs | Dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/v1/documents` | Register/upload or list governed documents | `POST`, `GET` | Required; curator/owner permissions | Document metadata and approved content/reference; filters for list | Document record, accepted pipeline status, or paginated summaries | Document, Authentication, Configuration | Not Implemented |
| `/v1/documents/{document_id}` | Inspect, update allowed metadata, restrict, or retire a document | `GET`, `PATCH`, `DELETE` | Required; owner/reviewer policy | Identifier, version/field changes, lifecycle intent | Document version/status or deletion outcome | Document, Authentication, Logging/audit | Not Implemented |
| `/v1/documents/{document_id}/versions` | List document versions and provenance | `GET` | Required according to document access | Identifier, pagination | Version metadata and provenance | Document | Not Implemented |
| `/v1/retrieval/search` | Retrieve permitted evidence without generation | `POST` | Required for scoped/private corpora | Query, domain/curriculum, filters, limits | Ranked chunks/documents and retrieval metadata | Retrieval, Document, Knowledge Graph | Not Implemented |
| `/v1/explanations` | Produce a grounded learning explanation | `POST` | Required for personalization; anonymous policy undecided | Question/task, domain scope, learner-safe context, response preferences | Explanation, uncertainty, Citations, version metadata | Retrieval, Generation, Citation, policy | Not Implemented |
| `/v1/citations/{citation_id}` | Resolve and inspect a citation | `GET` | Inherits source access policy | Citation identifier | Source locator, attribution, validation status | Citation, Document | Not Implemented |

## Learning and Assessment APIs

| Future API | Purpose | HTTP Method | Authentication Requirement | Expected Inputs | Expected Outputs | Dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/v1/study-sessions` | Start or list study sessions | `POST`, `GET` | Required | Domain, goal/scope, filters | Study Session or paginated summaries | Learning workflow, Domain, Authentication | Not Implemented |
| `/v1/study-sessions/{session_id}` | Inspect, update eligible state, complete, or abandon a session | `GET`, `PATCH`, `DELETE` | Required; owner policy | Identifier, version, allowed changes/status intent | Updated Study Session and summary | Learning workflow, Analytics | Not Implemented |
| `/v1/assessments` | List available assessments or create reviewer proposals | `GET`, `POST` | Required; creation needs curator role | Domain/curriculum filters or assessment proposal | Assessment summaries or proposed record | Question, Knowledge Graph, Authentication | Not Implemented |
| `/v1/assessments/{assessment_id}` | Retrieve assessment instructions and eligible items | `GET` | Required; access policy | Identifier, version | Assessment metadata and presentation contract | Question, Domain | Not Implemented |
| `/v1/questions/{question_id}` | Retrieve an authorized question or reviewer metadata | `GET` | Required | Identifier, context, version | Question presentation or reviewer view | Question, Authentication | Not Implemented |
| `/v1/questions/{question_id}/attempts` | Submit and list the user's attempts | `POST`, `GET` | Required; owner policy | Response, session/assessment context, confidence; list filters | Question Attempt, score/feedback when allowed, attempt history | Question, learning workflow, Analytics | Not Implemented |
| `/v1/knowledge-state` | Inspect explainable learner knowledge-state estimates | `GET` | Required; self/authorized reviewer | Domain, curriculum, concept filters, version/time | Knowledge State summaries, uncertainty, evidence references | ML inference, Question, Analytics, Knowledge Graph | Not Implemented |

## Recommendation and Revision APIs

| Future API | Purpose | HTTP Method | Authentication Requirement | Expected Inputs | Expected Outputs | Dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/v1/recommendations` | Request or list current recommendations | `POST`, `GET` | Required | Goal/domain context and constraints; filters | Ranked Recommendations with rationale and uncertainty | Recommendation, ML, Knowledge Graph | Not Implemented |
| `/v1/recommendations/{recommendation_id}` | Inspect, accept, dismiss, or report an outcome | `GET`, `PATCH` | Required; owner policy | Identifier, version, allowed decision/outcome | Updated Recommendation lifecycle | Recommendation, Analytics | Not Implemented |
| `/v1/revision-plans` | Create or list editable revision plans | `POST`, `GET` | Required | Goal, availability, accepted recommendation references; filters | Revision Plan or summaries | Revision, Recommendation, Knowledge Graph | Not Implemented |
| `/v1/revision-plans/{plan_id}` | Inspect, edit, or archive a plan | `GET`, `PATCH`, `DELETE` | Required; owner policy | Identifier, version, validated plan edits/lifecycle intent | Updated plan, conflicts, or archive outcome | Revision | Not Implemented |
| `/v1/revision-plans/{plan_id}/tasks/{task_id}` | Update a revision task lifecycle | `PATCH` | Required; owner policy | Task status, scheduling edit, completion evidence, version | Updated Revision Task and plan impact | Revision, Analytics | Not Implemented |

## Agent APIs

| Future API | Purpose | HTTP Method | Authentication Requirement | Expected Inputs | Expected Outputs | Dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/v1/agent-tasks` | Submit an approved bounded teacher/planner task | `POST` | Required; capability authorization | Role, task, domain, constraints, approved context, budget | Accepted task/status reference or synchronous result | Agents, application tools, policy | Not Implemented |
| `/v1/agent-tasks/{task_id}` | Inspect or cancel an agent task | `GET`, `DELETE` | Required; owner/administrator policy | Identifier, cancellation reason | Status, auditable steps summary, result or cancellation | Agents, Logging/audit | Not Implemented |
| `/v1/agent-tasks/{task_id}/approvals` | Approve or reject a gated agent action | `POST` | Required with action-specific authorization | Decision, expected action version, rationale | Approval outcome and resumed/terminated status | Agents, Authentication, Logging/audit | Not Implemented |

## Evaluation and Experiment APIs

| Future API | Purpose | HTTP Method | Authentication Requirement | Expected Inputs | Expected Outputs | Dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/v1/evaluations` | Submit or list authorized evaluation runs | `POST`, `GET` | Required; evaluator/operator role | Subject/data/configuration versions, metrics, thresholds; filters | Accepted run or paginated summaries | Evaluation, Experiment, Configuration | Not Implemented |
| `/v1/evaluations/{evaluation_id}` | Inspect status/result or cancel a run | `GET`, `DELETE` | Required; evaluator/operator policy | Identifier, cancellation reason | Evaluation Result/status or cancellation outcome | Evaluation, Logging | Not Implemented |
| `/v1/evaluations/{evaluation_id}/report` | Retrieve a traceable evaluation report | `GET` | Required; report access policy | Identifier, representation preference | Report and artifact references | Evaluation, artifact storage | Not Implemented |
| `/v1/experiments` | Register or list experiments | `POST`, `GET` | Required; researcher/evaluator role | Hypothesis, versions, owner, configuration; filters | Experiment record or summaries | Experiment, Configuration | Not Implemented |
| `/v1/experiments/{experiment_id}` | Inspect, update lifecycle, conclude, or archive an experiment | `GET`, `PATCH`, `DELETE` | Required; owner/reviewer policy | Identifier, version, status/conclusion or archive intent | Updated Experiment and linked results | Experiment, Evaluation, Logging | Not Implemented |

## Implementation

Empty. No route, schema, authentication mechanism, protocol framework, or server exists.

