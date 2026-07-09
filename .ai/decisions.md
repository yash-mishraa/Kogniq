# Architecture Decisions

This file is the Architecture Decision Record (ADR) log. ADRs are immutable historical records: superseded decisions remain and link to their replacements. New ADRs receive the next sequential number.

## ADR Template

### ADR-NNNN — `<TITLE>`

- **Status:** Proposed | Accepted | Rejected | Superseded
- **Date:** YYYY-MM-DD
- **Deciders:** Yash Mishra
- **Context:** What forces and constraints require a decision?
- **Decision:** What is being decided?
- **Alternatives Considered:** What credible options were evaluated?
- **Consequences:** What improves, what becomes harder, and what obligations follow?
- **Supersedes:** ADR-NNNN or None
- **Superseded By:** ADR-NNNN or None

## ADR-0001 — Use Version-Controlled AI Context Files

- **Status:** Accepted
- **Date:** 2026-07-09
- **Deciders:** Yash Mishra
- **Context:** The project, then using the legacy name **GATE Copilot**, is expected to evolve over many months with contributions from humans and multiple AI agents. Chat history is incomplete, transient, and difficult to review. Contributors need a concise, durable source for intent, boundaries, decisions, progress, and handoffs.
- **Decision:** Maintain an `.ai/` context system in version control. Every coding session must read the required context files before changing the repository and update progress and handoff information before finishing.
- **Alternatives Considered:** Rely on chat history; use only the root README; keep context in an external project-management tool.
- **Consequences:** Architectural memory becomes reviewable and travels with the code. Sessions require documentation discipline, files can become stale, and maintainers must resolve conflicts between context documents and implemented behavior. ADRs are authoritative for accepted decisions; `design.md` reflects the current architecture.
- **Supersedes:** None
- **Superseded By:** None

## ADR-0002 — Repository Rebranding to Kogniq

- **Status:** Accepted
- **Date:** 2026-07-09
- **Deciders:** Yash Mishra
- **Context:** The legacy name **GATE Copilot** framed the repository as a GATE-specific assistant. The intended system is broader: reusable learning intelligence, knowledge modeling, personalization, retrieval, evaluation, and agentic workflows should support multiple competitive-examination domains. Keeping the old identity would encourage GATE-specific assumptions in platform contracts and obscure the distinction between reusable capabilities and domain content.
- **Decision:** Rename the product and repository identity to **Kogniq**, described as an **AI Learning Intelligence Platform**. Treat GATE as the first planned learning-domain plugin and reference implementation, not as the product. Keep the platform core examination-neutral and require future domains to integrate through explicit, versioned extension contracts. GRE, CAT, UPSC, JEE, and NEET are illustrative future domains only; this decision does not authorize or implement their support.
- **Alternatives Considered:** Retain GATE Copilot and later generalize it; create separate products for each examination; use Kogniq as an umbrella brand while retaining a GATE-specific core.
- **Consequences:** Product language and architecture now clearly separate platform capabilities from domain knowledge. Future designs must define plugin compatibility, ownership, isolation, and domain-specific evaluation. The broader scope increases design obligations and makes domain leakage a review concern. Historical references to GATE Copilot must be labeled as legacy rather than silently rewritten.
- **Supersedes:** None
- **Superseded By:** None

## ADR-0003 — System Blueprint Introduced

- **Status:** Accepted
- **Date:** 2026-07-09
- **Deciders:** Yash Mishra
- **Context:** Kogniq's living architecture defined principles and capability boundaries, but future implementation still lacked one engineering specification connecting package ownership, logical services, pipelines, data and knowledge flows, AI lifecycle, deployment concerns, and extension rules. Implementing directly from scattered plans would invite inconsistent boundaries, accidental microservices, domain leakage, and technology choices made before requirements.
- **Decision:** Adopt `.ai/system_blueprint.md` as Kogniq's master engineering specification and require agents to read it before implementing code. Maintain supporting package, service, pipeline, and API catalogs as planning inventories. Catalog entries do not create packages, services, endpoints, infrastructure, or implementation status. Physical repository restructuring and technology selection remain separate future decisions.
- **Alternatives Considered:** Rely only on `design.md`; document architecture inside future code; let each package define boundaries independently; create implementation scaffolding first and infer contracts afterward.
- **Consequences:** Contributors gain a common map for responsibilities, dependencies, flows, and extension decisions before code exists. The blueprint and catalogs require active maintenance and can become misleading if planned and implemented status are conflated. Significant blueprint changes must follow the architecture decision flow, and implementation must still validate assumptions through requirements, experiments, and ADRs.
- **Supersedes:** None
- **Superseded By:** None

## ADR-0004 — Adopt Physical Modular Monorepo Workspace

- **Status:** Accepted
- **Date:** 2026-07-09
- **Deciders:** Yash Mishra
- **Context:** ADR-0003 defined future `apps/*`, `packages/*`, and `infrastructure` contracts while the repository still used Stage 0 top-level capability placeholders. Beginning engineering work with two competing layouts would create ambiguous ownership, broken dependency guidance, and later migration cost.
- **Decision:** Adopt `apps/api`, `apps/web`, `packages/shared`, `packages/domain`, `packages/rag`, `packages/ml`, `packages/agents`, `packages/knowledge_graph`, `packages/evaluation`, and `infrastructure` as the physical modular-monorepo workspace. Retain cross-cutting documentation, datasets, experiments, scripts, and tests at the repository root. Remove superseded documentation-only capability directories after preserving their guidance. Do not select a language workspace, package manager, dependency, framework, service topology, or deployment technology in this decision.
- **Alternatives Considered:** Keep both legacy and planned directories; defer physical layout until framework selection; organize entirely by technical layer; create independently deployable repositories.
- **Consequences:** Physical paths now match package contracts and clarify dependency direction before source exists. The `packages/domain` boundary makes business contexts explicit. Future tooling can be selected without another structural migration, but workspace manifests must wait for technology decisions. Existing references and contributor habits must use the new paths.
- **Supersedes:** None
- **Superseded By:** None

## ADR-0005 — Adopt uv-Based Python Engineering Toolchain

- **Status:** Accepted
- **Date:** 2026-07-09
- **Deciders:** Yash Mishra
- **Context:** Stage 1 requires a reproducible Python engineering foundation before application or intelligence packages are implemented. The repository needs one source for supported Python versions, dependency groups, formatting, linting, typing, test discovery, and coverage policy without selecting product frameworks or creating independently configured package islands.
- **Decision:** Target Python 3.12–3.13 and use uv for the root project, workspace membership, dependency lifecycle, and developer command execution. Centralize Ruff, strict MyPy, pytest, and coverage.py configuration in `pyproject.toml`. Keep the root project non-packaged and add package directories as uv workspace members only when their Python distribution boundaries are approved. Permit minimal standard-library scaffolding in `packages/shared` for configuration, logging, generic exceptions, and broadly reusable provider protocols.
- **Alternatives Considered:** pip and virtualenv; Poetry; Pipenv; PDM or Hatch; per-package tool configuration; separate Black, Flake8, and isort tools; Pyright; delaying Python standards until API implementation.
- **Consequences:** Future Python work receives consistent local commands and quality policy with no runtime dependency. Development tools remain an explicit dev group and require `uv sync` before first use. The repository must maintain Python 3.12 compatibility, avoid package-specific configuration drift, and keep generic shared abstractions small. Non-Python workspaces will require separate evidence-backed decisions.
- **Supersedes:** None
- **Superseded By:** None
