# Technology Stack Register

No library or vendor is finalized during Stage 0. A choice becomes **Chosen** only after requirements, alternatives, evaluation evidence, and an ADR exist.

## Backend

- **Chosen:** Not selected.
- **Alternatives:** Python frameworks; TypeScript frameworks; other evidence-backed server platforms.
- **Reason:** Domain boundaries, latency, deployment, and team constraints are not yet defined.
- **Current Status:** Deferred.

## Frontend

- **Chosen:** Not selected.
- **Alternatives:** React-based frameworks; other accessible web frameworks.
- **Reason:** Rendering, accessibility, offline, and interaction requirements require discovery.
- **Current Status:** Deferred.

## ML

- **Chosen:** Not selected.
- **Alternatives:** Major Python ML ecosystems; managed or self-hosted inference.
- **Reason:** Tasks, baselines, data scale, and deployment constraints remain unknown.
- **Current Status:** Deferred.

## Vector DB

- **Chosen:** Not selected.
- **Alternatives:** Database extensions; dedicated vector stores; managed search services.
- **Reason:** Corpus scale, filtering, recall, latency, operations, and cost must be benchmarked.
- **Current Status:** Deferred.

## Knowledge Graph

- **Chosen:** Not selected.
- **Alternatives:** Graph databases; relational graph modeling; RDF stores.
- **Reason:** Query patterns, ontology standards, scale, and interoperability need definition.
- **Current Status:** Deferred.

## Experiment Tracking

- **Chosen:** Not selected.
- **Alternatives:** Open-source tracking platforms; managed platforms; lightweight metadata standards.
- **Reason:** Reproducibility, artifact, governance, and hosting needs are not established.
- **Current Status:** Deferred.

## Deployment

- **Chosen:** Not selected.
- **Alternatives:** Managed platform services; containers; orchestrated containers; serverless workloads.
- **Reason:** Traffic, reliability, compliance, skills, and budget targets are unknown.
- **Current Status:** Deferred.

## Testing

- **Chosen:** No framework selected.
- **Alternatives:** Language-native unit, integration, contract, browser, model, and evaluation frameworks.
- **Reason:** Framework choices follow selected runtimes; testing expectations are defined in `coding_rules.md`.
- **Current Status:** Policy defined; tooling deferred.

## CI/CD

- **Chosen:** Not selected.
- **Alternatives:** GitHub-hosted workflows; other managed or self-hosted automation.
- **Reason:** Repository hosting, security, release, and deployment requirements need confirmation.
- **Current Status:** Deferred.

## Observability

- **Chosen:** Not selected.
- **Alternatives:** Open standards with self-hosted or managed telemetry backends.
- **Reason:** SLOs, data sensitivity, retention, and cost requirements are not defined.
- **Current Status:** Deferred.

