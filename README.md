# Kogniq

Kogniq is a planned open-source AI Learning Intelligence Platform. Its long-term purpose is to combine rigorous learning workflows with production-grade AI engineering, including retrieval, knowledge tracing, recommendations, agentic systems, evaluation, and MLOps.

Kogniq is designed as a domain-neutral platform. GATE is the first planned learning-domain plugin and reference implementation—not the product itself. Future domains may include GRE, CAT, UPSC, JEE, and NEET, but none of these integrations has been implemented.

## Project Status

**Stage 1 — Monorepo Foundation.** The engineering workspace and documentation contracts exist. No application, infrastructure, data, API, UI, or model functionality has been implemented, and no dependency tooling has been selected.

## Architecture Overview

The planned platform separates domain-neutral learning intelligence from pluggable examination content and rules, user experience, application services, knowledge systems, and operational concerns. Boundaries and dependencies are documented in [`.ai/design.md`](.ai/design.md); technology choices remain intentionally undecided.

## Repository Structure

| Path | Planned responsibility |
| --- | --- |
| `.ai/` | Durable context, architecture, decisions, and handoffs |
| `apps/api/` | Future application workflows and external contracts |
| `apps/web/` | Future accessible browser experience |
| `packages/shared/` | Minimal reusable contracts and primitives |
| `packages/domain/` | Examination-neutral bounded contexts |
| `packages/ml/` | Future predictive models and knowledge tracing |
| `packages/rag/` | Future retrieval and grounded generation |
| `packages/agents/` | Future bounded agent orchestration |
| `packages/knowledge_graph/` | Future concept graph models and pipelines |
| `packages/evaluation/` | Future quality and release evaluation |
| `infrastructure/` | Reserved operational boundary; no implementation |
| `datasets/` | Dataset documentation and governed manifests |
| `experiments/` | Reproducible research experiments |
| `scripts/` | Repository-wide operational utilities |
| `docs/` | User, developer, and operational documentation |
| `tests/` | Cross-module and end-to-end tests |
| `.github/` | Future GitHub collaboration and CI configuration |

Workspace dependency rules and tooling status are summarized in [`WORKSPACE.md`](WORKSPACE.md).

## Roadmap Summary

The roadmap progresses from repository planning through infrastructure foundations, product surfaces, intelligence systems, integration, hardening, and production deployment. Milestones and completion criteria are maintained in [`.ai/roadmap.md`](.ai/roadmap.md).

## How AI Agents Should Work

Before making changes, every AI agent must follow [`.ai/handoff.md`](.ai/handoff.md), read the required context files, respect recorded decisions, and update progress before ending a session.

## Future Modules

Planned modules include domain plugins, learning workflows, content and assessment services, retrieval-augmented tutoring, knowledge graphs, learner modeling, recommendations, agent orchestration, and continuous evaluation. GATE will be the first reference domain; other competitive examinations may be supported through the same future domain contract. These are plans, not current capabilities.

## Contributing

Contribution guidance is currently a planning placeholder. See [`.ai/contributing.md`](.ai/contributing.md). Repository URL: `<GITHUB_URL>`. Contact: `<CONTACT_EMAIL>`.

## License

License: `<LICENSE>`.
