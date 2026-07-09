# Planned Service Catalog

These are logical capabilities, not deployed microservices. Multiple services may initially share `apps/api` or package runtimes. Extraction requires architectural evidence and an ADR. Data terms follow [`data_dictionary.md`](data_dictionary.md); package ownership follows [`package_contracts.md`](package_contracts.md).

## Document Service

- **Purpose:** Govern source documents, rights, provenance, versions, access, and ingestion status.
- **Inputs:** Authorized uploads or source references, domain context, ownership, license, metadata.
- **Outputs:** Document records, versions, status, provenance, retirement/deletion events.
- **Dependencies:** Authentication/authorization, Configuration, Logging, artifact scanning and storage adapters.
- **Future APIs:** Register, upload, inspect, list versions, publish, restrict, retire, and delete documents.
- **Future Storage:** Authoritative document metadata plus governed object storage; technology undecided.

## Chunk Service

- **Purpose:** Produce and govern addressable document segments.
- **Inputs:** Approved document version, extraction output, chunk policy and version.
- **Outputs:** Ordered chunks, structural locations, derivation metadata, invalidation events.
- **Dependencies:** Document, Configuration, Logging; parser and artifact adapters.
- **Future APIs:** Start derivation, inspect chunks, query status, invalidate, and regenerate.
- **Future Storage:** Derived chunk metadata/content with source lineage; technology undecided.

## Embedding Service

- **Purpose:** Generate versioned vector representations for eligible objects.
- **Inputs:** Authorized source object/version, model/configuration version, task context.
- **Outputs:** Embedding record, dimensions, model metadata, usage, failure status.
- **Dependencies:** Chunk or source owner, Configuration, Logging, model adapter.
- **Future APIs:** Embed one or batch, inspect capability, status, invalidate by model/source.
- **Future Storage:** Vector representations and lineage, possibly separate from authoritative source records.

## Retrieval Service

- **Purpose:** Select and rank permitted evidence for a query.
- **Inputs:** Query, domain/curriculum scope, authorization filters, retrieval policy, limits.
- **Outputs:** Ranked candidates, scores, provenance, applied filters, retrieval metadata.
- **Dependencies:** Document, Chunk, Embedding, Knowledge Graph, Configuration, Logging.
- **Future APIs:** Retrieve, explain retrieval metadata, list capabilities, and health/status.
- **Future Storage:** Search indexes and optional bounded caches; no authoritative source ownership.

## Generation Service

- **Purpose:** Produce structured or natural-language output under grounded policies.
- **Inputs:** Authorized task, instructions, evidence context, learner-appropriate settings, model policy.
- **Outputs:** Generated result, uncertainty, evidence links, model/configuration metadata, usage.
- **Dependencies:** Retrieval, Citation, Configuration, Logging, model adapter, runtime safety checks.
- **Future APIs:** Generate grounded explanation, transform content, stream result, cancel request.
- **Future Storage:** Minimal eligible provenance and audit metadata; avoid unnecessary prompt retention.

## Citation Service

- **Purpose:** Assemble and validate traceable claim-to-source references.
- **Inputs:** Output claims/spans, retrieved chunks, document versions, citation policy.
- **Outputs:** Citations, validation findings, unsupported-claim flags, source availability status.
- **Dependencies:** Document, Chunk, Retrieval, Configuration, Logging.
- **Future APIs:** Create, validate, resolve, and inspect citations.
- **Future Storage:** Citation relationships and validation status tied to dependent output lifecycle.

## Knowledge Graph Service

- **Purpose:** Govern graph entities, relationships, curricula, provenance, versions, and queries.
- **Inputs:** Reviewed node/edge proposals, domain namespace, evidence, graph queries.
- **Outputs:** Versioned graph changes, traversals, concept relationships, validation reports.
- **Dependencies:** Authentication/authorization, Document provenance, Configuration, Logging, domain plugins.
- **Future APIs:** Query nodes/edges, traverse, validate proposal, publish version, inspect provenance.
- **Future Storage:** Logical graph store and version/provenance metadata; technology undecided.

## Question Service

- **Purpose:** Govern assessment items, concept mappings, scoring specifications, and review state.
- **Inputs:** Authored or proposed questions, domain/curriculum version, provenance, reviewer decisions.
- **Outputs:** Versioned questions, approved mappings, scoring results/specifications, status events.
- **Dependencies:** Knowledge Graph, Document, Authentication/authorization, Configuration, Logging.
- **Future APIs:** Create proposal, review, publish, retrieve, submit attempt, inspect feedback.
- **Future Storage:** Question versions, mappings, review history, and attempt references.

## Recommendation Service

- **Purpose:** Rank and explain suitable next learning actions.
- **Inputs:** Authorized learner goal, knowledge state, curriculum scope, candidates, constraints.
- **Outputs:** Ranked recommendations, rationale, evidence, uncertainty, model/rule version.
- **Dependencies:** Question, Knowledge Graph, Analytics, Configuration, Logging, ML inference.
- **Future APIs:** Request, list, accept, dismiss, explain, and report outcome.
- **Future Storage:** Recommendation lifecycle and provenance; source learner data remains owner-scoped.

## Revision Service

- **Purpose:** Govern editable revision plans and tasks.
- **Inputs:** Learner goals, accepted recommendations, availability, concept needs, user edits.
- **Outputs:** Versioned plans/tasks, schedules, status changes, completion evidence.
- **Dependencies:** Recommendation, Question, Knowledge Graph, Configuration, Logging.
- **Future APIs:** Create, inspect, edit, schedule, complete, skip, and archive revision work.
- **Future Storage:** Revision plans, task lifecycle, and user-authored adjustments.

## Analytics Service

- **Purpose:** Produce privacy-governed operational and learning aggregates.
- **Inputs:** Approved events, data classification, metric definitions, consent and retention policy.
- **Outputs:** Aggregates, trends, quality indicators, anomaly signals; no hidden learner scoring.
- **Dependencies:** Configuration, Logging, Authentication/authorization, governed event producers.
- **Future APIs:** Query approved metrics, inspect definitions, export aggregate reports.
- **Future Storage:** De-identified or access-controlled analytical data with lineage and retention.

## Evaluation Service

- **Purpose:** Run reproducible evaluations and enforce approved quality gates.
- **Inputs:** Versioned subject, dataset, metrics, slices, configuration, threshold policy.
- **Outputs:** Evaluation Result, artifacts, failures, comparisons, gate decision.
- **Dependencies:** Experiment, Configuration, Logging, artifact storage, public interfaces of evaluated subjects.
- **Future APIs:** Submit run, status, cancel, retrieve result/report, compare runs.
- **Future Storage:** Evaluation metadata, results, reports, and governed artifacts.

## Authentication Service

- **Purpose:** Establish identity and session assurance for protected workflows.
- **Inputs:** Credentials or identity-provider assertions, session context, authentication policy.
- **Outputs:** Verified principal, session/token metadata, authentication events and failures.
- **Dependencies:** Configuration, Logging/audit, approved identity provider and secret delivery.
- **Future APIs:** Sign in, sign out, refresh, session status, recovery, and identity linking as approved.
- **Future Storage:** Minimal identity/session/security records; design deferred to its roadmap stage.

## Configuration Service

- **Purpose:** Supply validated, versioned, scoped runtime behavior settings.
- **Inputs:** Environment configuration, approved feature decisions, secret references, policy versions.
- **Outputs:** Effective typed configuration, version metadata, validation errors, change events.
- **Dependencies:** Secret delivery, Logging/audit, environment management.
- **Future APIs:** Read permitted configuration, inspect version, validate proposed change; privileged mutation only if approved.
- **Future Storage:** Non-secret configuration and audit history; secrets remain in an approved secret system.

## Logging Service

- **Purpose:** Receive structured operational telemetry and security audit events.
- **Inputs:** Classified logs, metrics, traces, audit records, correlation and ownership context.
- **Outputs:** Searchable telemetry, alerts, dashboards, retention/deletion outcomes.
- **Dependencies:** Configuration, identity context, telemetry backends.
- **Future APIs:** Standard telemetry ingestion and authorized query/export interfaces.
- **Future Storage:** Segregated operational telemetry and immutable audit records with distinct retention.

## Experiment Service

- **Purpose:** Track reproducible investigations and their artifact lineage.
- **Inputs:** Hypothesis, owner, configuration, code/data/model versions, run status.
- **Outputs:** Experiment record, artifacts, metrics links, comparison, conclusion.
- **Dependencies:** Evaluation, Configuration, Logging, artifact and metadata adapters.
- **Future APIs:** Register, start, update status, attach artifact/result, compare, conclude, archive.
- **Future Storage:** Experiment metadata and references to governed artifacts; not production truth.

