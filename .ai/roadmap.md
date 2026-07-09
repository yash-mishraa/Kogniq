# Roadmap

Roadmap statuses: **Not Started**, **In Progress**, **Blocked**, or **Complete**. Stages describe milestones, not implementation instructions.

## Stage 0 — Repository Planning

- **Status:** Complete
- **Description:** Establish repository boundaries, durable AI context, governance, and contribution expectations.
- **Dependencies:** None.
- **Completion Criteria:** Requested skeleton and context documents exist, ownership is explicit, and initialization is reviewed.

## Stage 1 — Infrastructure Foundations

- **Status:** In Progress
- **Description:** Establish the modular monorepo workspace, then define local development, environments, configuration, delivery foundations, and baseline observability through separately authorized prompts.
- **Dependencies:** Stage 0.
- **Completion Criteria:** Approved infrastructure ADRs and reproducible development baseline.

## Stage 2 — Backend Foundations

- **Status:** Not Started
- **Description:** Establish domain boundaries and stable application contracts.
- **Dependencies:** Stages 0–1.
- **Completion Criteria:** Approved service boundaries and a tested foundation for domain workflows.

## Stage 3 — Frontend Foundations

- **Status:** Not Started
- **Description:** Establish accessible user-experience architecture and backend integration conventions.
- **Dependencies:** Backend contracts and infrastructure baseline.
- **Completion Criteria:** Tested frontend foundation meeting accessibility and quality gates.

## Stage 4 — Knowledge and Data Foundations

- **Status:** Not Started
- **Description:** Establish governed datasets, content lifecycle, ontology, knowledge graph foundations, and a domain-neutral contract for examination plugins. Validate the contract with a planned GATE reference domain without coupling the platform core to it.
- **Dependencies:** Stages 1–2; approved data governance.
- **Completion Criteria:** Versioned, validated knowledge, data, and domain-extension contracts with documented provenance and explicit core/plugin boundaries.

## Stage 5 — Retrieval-Augmented Learning

- **Status:** Not Started
- **Description:** Introduce grounded retrieval and evidence-aware learning assistance.
- **Dependencies:** Stage 4 and an evaluation baseline.
- **Completion Criteria:** Retrieval and grounding meet approved offline quality thresholds.

## Stage 6 — Learner Modeling and Recommendations

- **Status:** Not Started
- **Description:** Introduce knowledge tracing and recommendation capabilities based on governed learner signals.
- **Dependencies:** Stages 2 and 4; consent and privacy requirements.
- **Completion Criteria:** Models outperform approved baselines and satisfy fairness, privacy, and monitoring gates.

## Stage 7 — Agentic Workflows

- **Status:** Not Started
- **Description:** Add bounded agents where tool use materially improves learning or operations.
- **Dependencies:** Stable backend tools, evaluation, security controls, and Stages 5–6 as applicable.
- **Completion Criteria:** Agent workflows are constrained, auditable, recoverable, and pass safety evaluations.

## Stage 8 — Integrated Evaluation and Hardening

- **Status:** Not Started
- **Description:** Validate the complete platform for correctness, learning quality, security, reliability, accessibility, and cost.
- **Dependencies:** Product capabilities intended for release.
- **Completion Criteria:** Release gates, SLOs, threat review, load tests, and rollback exercises pass.

## Stage 9 — Production Deployment

- **Status:** Not Started
- **Description:** Release an observable, supportable production platform through controlled rollout.
- **Dependencies:** Stage 8 and operational approval.
- **Completion Criteria:** Deployment is complete, monitored, documented, reversible, and ownership is accepted.
