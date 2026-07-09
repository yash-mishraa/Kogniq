# Planned Package Contracts

These contracts govern the documentation-only workspace directories created in Stage 1. No language package, framework, dependency, or deployment unit exists yet. Shared terms follow [`glossary.md`](glossary.md); architectural rules follow [`system_blueprint.md`](system_blueprint.md).

## Contract Rules

- Public interfaces are the only supported cross-package dependency points.
- Internal modules and storage are private to their owner.
- Contracts are versioned, typed, validated at runtime where data is untrusted, and covered by compatibility tests.
- Expected APIs are capability shapes, not HTTP commitments. HTTP inventory is in [`api_catalog.md`](api_catalog.md).
- Configuration is validated, documented, secret-free by default, and scoped to the owning package.

## `apps/api`

- **Purpose:** Provide authoritative application workflows and external service contracts.
- **Responsibilities:** Request validation, authentication integration, authorization, workflow orchestration, idempotency, error translation, and transaction boundaries.
- **Public Interfaces:** Versioned application commands, queries, events, health/readiness contracts, and approved agent tool contracts.
- **Allowed Dependencies:** `packages/shared` and public interfaces of domain, ML, RAG, agents, knowledge graph, and approved domain plugins.
- **Forbidden Dependencies:** `apps/web`; package internals; experiment code; evaluation implementation; direct access to another owner's storage; provider SDKs outside adapters.
- **Future Modules:** Learning sessions, documents, questions, attempts, recommendations, revision, domains, users, policy, and application adapters.
- **Ownership:** Backend/platform team — `<OWNER_NAME>`.
- **Expected Tests:** Unit, authorization, contract, integration, idempotency, failure, migration compatibility, and end-to-end workflow tests.
- **Expected Documentation:** Public behavior, error semantics, authorization matrix, events, operational runbooks, and migration notes.
- **Expected APIs:** Cataloged learner, content, assessment, recommendation, evaluation administration, and system-status APIs.
- **Expected Configuration:** Bind address, timeouts, limits, feature decisions, dependency endpoints, and secret references; no embedded credentials.

## `apps/web`

- **Purpose:** Deliver accessible learner, reviewer, and operator experiences.
- **Responsibilities:** Presentation, interaction state, client validation, accessibility, progressive feedback, safe rendering, and consumption of supported application APIs.
- **Public Interfaces:** Routes, UI components intended for reuse, client telemetry schema, and API-client boundary.
- **Allowed Dependencies:** `packages/shared` browser-safe contracts and generated or maintained clients for `apps/api`.
- **Forbidden Dependencies:** Server internals, databases, ML/RAG/agent internals, secrets, privileged provider SDKs, or direct domain-plugin execution.
- **Future Modules:** Learning workspace, curriculum explorer, assessment player, progress, revision planner, reviewer console, settings, and accessibility preferences.
- **Ownership:** Frontend/product experience team — `<OWNER_NAME>`.
- **Expected Tests:** Component, accessibility, interaction, API-contract, browser, visual regression, security, and critical-journey tests.
- **Expected Documentation:** Supported browsers, accessibility behavior, state ownership, design-system usage, error states, and user journeys.
- **Expected APIs:** Calls only documented `apps/api` interfaces; may expose no independent product API.
- **Expected Configuration:** Public runtime endpoints, locale, safe feature decisions, and telemetry policy; never secrets.

## `packages/ml`

- **Purpose:** Own reusable learner-modeling, ranking, training, and inference capabilities.
- **Responsibilities:** Task definitions, features, knowledge tracing, recommendation scoring, model adapters, training, validation, registration metadata, and monitoring signals.
- **Public Interfaces:** Versioned training and inference requests/results, model metadata, feature contracts, and health/capability descriptions.
- **Allowed Dependencies:** `packages/shared`; approved data and model adapters; public knowledge-graph query contracts when required.
- **Forbidden Dependencies:** UI, API workflow internals, RAG internals, agent orchestration, domain-specific hardcoding, or direct ownership of user workflows.
- **Future Modules:** Knowledge tracing, ranking, calibration, feature processing, training, inference, registry adapters, and drift monitoring.
- **Ownership:** ML engineering and applied science — `<OWNER_NAME>`.
- **Expected Tests:** Unit, property, data-contract, reproducibility, baseline comparison, calibration, fairness, performance, and model-regression tests.
- **Expected Documentation:** Model cards, task definitions, data declarations, feature lineage, metrics, limitations, inference contract, and rollback guidance.
- **Expected APIs:** Internal inference and training capabilities; external exposure only through `apps/api`.
- **Expected Configuration:** Model/artifact references, resource limits, timeouts, feature versions, thresholds, and safe provider settings.

## `packages/rag`

- **Purpose:** Own governed ingestion, retrieval, grounding, generation, and citation capabilities.
- **Responsibilities:** Parsing coordination, chunking, embedding, indexing, querying, filtering, reranking, context assembly, generation adapters, and citation validation.
- **Public Interfaces:** Ingestion commands/status, retrieval queries/results, grounded-generation requests/results, citations, and capability metadata.
- **Allowed Dependencies:** `packages/shared`; public knowledge-graph queries; approved model, parser, index, and artifact adapters.
- **Forbidden Dependencies:** Application authorization decisions, frontend code, learner workflow ownership, agent planning, domain hardcoding, or private storage from other packages.
- **Future Modules:** Document ingestion, chunking, embeddings, indexes, hybrid retrieval, reranking, context building, generation, citation validation, and RAG evaluation hooks.
- **Ownership:** Retrieval and AI engineering — `<OWNER_NAME>`.
- **Expected Tests:** Parser fixtures, chunk invariants, retrieval relevance, filtering, citation integrity, prompt-injection defense, provider contracts, performance, and regression evaluations.
- **Expected Documentation:** Supported inputs, provenance, indexing lifecycle, retrieval semantics, grounding guarantees, failure modes, and evaluation methodology.
- **Expected APIs:** Internal ingestion, retrieval, generation, and citation capabilities; application access through `apps/api`.
- **Expected Configuration:** Parser and model references, chunk policy, index selection, retrieval limits, filters, timeouts, and generation policy.

## `packages/agents`

- **Purpose:** Own bounded agent workflows, tool use, state policies, and safeguards.
- **Responsibilities:** Role definitions, orchestration, approved tool registry, planning limits, memory policy, budgets, audit context, recovery, and agent evaluation hooks.
- **Public Interfaces:** Versioned agent task requests/results, tool contracts, execution events, approvals, and cancellation.
- **Allowed Dependencies:** `packages/shared` and approved application tool contracts; public intelligence contracts only when explicitly mediated.
- **Forbidden Dependencies:** Direct database access, private package internals, unapproved network/tool access, embedded domain behavior, or authority to bypass application policy.
- **Future Modules:** Teacher Agent, Planner Agent, reviewer assistant, tool registry, policy engine, execution state, budget enforcement, and audit adapters.
- **Ownership:** Agentic AI team with security review — `<OWNER_NAME>`.
- **Expected Tests:** Deterministic policy, tool-contract, authorization, budget, cancellation, timeout, injection, recovery, adversarial, and behavior-evaluation tests.
- **Expected Documentation:** Role and tool permissions, termination conditions, state retention, human approval points, risks, and evaluation evidence.
- **Expected APIs:** Internal task submission, status, cancellation, and approval interfaces exposed through authorized `apps/api` workflows.
- **Expected Configuration:** Allowed roles/tools, step and cost budgets, timeouts, model policy, memory retention, and safety thresholds.

## `packages/knowledge_graph`

- **Purpose:** Own the domain-neutral graph model and governed domain extensions.
- **Responsibilities:** Ontology contracts, graph validation, curriculum mappings, versioning, provenance, graph ingestion, and query behavior.
- **Public Interfaces:** Node/edge schemas, versioned graph queries, traversal results, validation reports, and import/export contracts.
- **Allowed Dependencies:** `packages/shared`; governed domain-plugin contracts; approved graph persistence adapters.
- **Forbidden Dependencies:** Product workflow internals, UI, model training implementation, RAG internals, or assumptions tied to one examination.
- **Future Modules:** Ontology, schema validation, curriculum mapping, graph builder, traversal, provenance, version migration, and storage adapters.
- **Ownership:** Knowledge engineering with domain reviewers — `<OWNER_NAME>`.
- **Expected Tests:** Schema, invariant, provenance, traversal, version compatibility, domain isolation, import/export, and performance tests.
- **Expected Documentation:** Ontology guide, relationship semantics, provenance rules, query contracts, versioning, and domain extension guidance.
- **Expected APIs:** Internal graph query and curation capabilities; authorized external access through `apps/api`.
- **Expected Configuration:** Active graph version, domain namespaces, validation policy, query limits, and storage adapter settings.

## `packages/evaluation`

- **Purpose:** Independently measure product, model, retrieval, graph, agent, safety, and learning quality.
- **Responsibilities:** Dataset manifests, metrics, rubrics, harnesses, slices, thresholds, reports, adjudication support, and release gates.
- **Public Interfaces:** Evaluation specifications, run requests, result schemas, threshold decisions, and report artifacts.
- **Allowed Dependencies:** `packages/shared`; public interfaces or black-box endpoints of evaluated subjects; governed dataset and artifact adapters.
- **Forbidden Dependencies:** Production runtime as a required library dependency, mutation of evaluated subject internals, training-data leakage, or hidden release exceptions.
- **Future Modules:** Dataset registry, runners, metrics, human review, statistical analysis, report generation, regression comparison, and gate policy.
- **Ownership:** Evaluation team with product, subject, safety, and ML reviewers — `<OWNER_NAME>`.
- **Expected Tests:** Metric correctness, fixture integrity, runner reproducibility, leakage checks, threshold logic, report stability, and harness contract tests.
- **Expected Documentation:** Methodology, dataset cards, metric interpretation, slices, limitations, thresholds, reviewer guidance, and reproducibility instructions.
- **Expected APIs:** Evaluation submission, status, result, and report interfaces for authorized operators; no learner-facing authority.
- **Expected Configuration:** Dataset and subject versions, metrics, slices, thresholds, resource budgets, reviewer policy, and artifact destinations.

## `packages/shared`

- **Purpose:** Hold minimal stable contracts and primitives genuinely shared across boundaries.
- **Responsibilities:** Cross-package identifiers, result/error envelopes, correlation context, pagination, time/version primitives, contract metadata, and validation-neutral schemas.
- **Public Interfaces:** Entire package surface is public and deliberately small; every export requires ownership and compatibility review.
- **Allowed Dependencies:** Language/runtime standard facilities and narrowly justified contract-validation libraries.
- **Forbidden Dependencies:** Product business rules, provider SDKs, storage clients, framework-specific application code, domain-specific types, or imports from any other Kogniq package.
- **Future Modules:** Identifiers, errors, result types, metadata, pagination, provenance, compatibility, telemetry context, and contract test utilities.
- **Ownership:** Architecture/platform maintainers — `<OWNER_NAME>`.
- **Expected Tests:** Serialization, validation, compatibility, property, platform portability, and consumer contract tests.
- **Expected Documentation:** Export rationale, semantic guarantees, version policy, examples, compatibility rules, and deprecation process.
- **Expected APIs:** In-process/shared contract definitions only; no independent network API.
- **Expected Configuration:** None where possible; shared contracts must not read environment state.

## `packages/domain`

- **Purpose:** Own examination-neutral business language, invariants, and bounded-context contracts.
- **Responsibilities:** Separate learning, assessment, student, documents, analytics, and recommendation semantics; define context ownership and future ports.
- **Public Interfaces:** Future entities, value semantics, use cases, domain events, and ports explicitly published by each bounded context.
- **Allowed Dependencies:** `packages/shared` only; cross-context collaboration through approved public contracts.
- **Forbidden Dependencies:** Applications, delivery frameworks, databases/ORMs, provider SDKs, intelligence implementations, infrastructure, and examination-specific hardcoding.
- **Future Modules:** `learning`, `assessment`, `student`, `documents`, `analytics`, and `recommendation`.
- **Ownership:** Domain architecture with affected capability owners — `<OWNER_NAME>`.
- **Expected Tests:** Invariant, value, state-transition, contract, context-boundary, and domain-event tests.
- **Expected Documentation:** Ubiquitous language, invariants, context maps, public contracts, examples, and decision rationale.
- **Expected APIs:** Framework-neutral domain ports only; external APIs remain owned by `apps/api`.
- **Expected Configuration:** None in the domain core; behavior-changing policy enters through explicit typed inputs or domain-plugin contracts.

## `infrastructure`

- **Purpose:** Define future build, runtime, deployment, environment, security, and observability resources.
- **Responsibilities:** Environment topology, artifact delivery, workload configuration, network and identity policy, secrets integration, telemetry, backup, recovery, and deployment controls.
- **Public Interfaces:** Environment outputs, deployment inputs, operational contracts, dashboards, alerts, and runbook references.
- **Allowed Dependencies:** Approved deployment tooling, platform providers, application artifacts, and explicit configuration schemas.
- **Forbidden Dependencies:** Product business logic, domain rules, embedded secrets, source-code forks per environment, or undocumented manual state.
- **Future Modules:** Environments, networking, compute, persistence, secret delivery, observability, backup, policy, and deployment automation.
- **Ownership:** Platform/infrastructure team — `<OWNER_NAME>`.
- **Expected Tests:** Static validation, policy, security, plan/diff review, ephemeral integration, backup/restore, rollback, and disaster-recovery exercises.
- **Expected Documentation:** Environment model, threat boundaries, deployment and rollback, runbooks, ownership, cost, recovery, and access procedures.
- **Expected APIs:** Operational provider interfaces and environment outputs only; no product API.
- **Expected Configuration:** Environment-specific non-secret values, secret references, resource limits, regions, retention, alerts, and release policy.
