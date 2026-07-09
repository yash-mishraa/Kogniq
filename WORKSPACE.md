# Kogniq Workspace Strategy

Kogniq uses a modular monorepo organized around deployable applications, reusable packages, governed infrastructure, and cross-cutting engineering support.

## Workspace Boundaries

- `apps/` contains future composition roots and user-facing application surfaces.
- `packages/` contains reusable capability and domain packages with explicit public contracts.
- `infrastructure/` reserves future operational definitions; it contains no infrastructure implementation at this stage.
- `docs/`, `.ai/`, `scripts/`, `tests/`, `datasets/`, and `experiments/` support the workspace without becoming production package dependencies.

## Dependency Direction

Applications may compose public package interfaces. Packages may depend on `packages/shared` and on explicitly allowed public contracts recorded in [`.ai/package_contracts.md`](.ai/package_contracts.md). Domain contexts remain inward-facing and independent of delivery frameworks. Circular dependencies, imports from application code into packages, and production dependencies on experiments are prohibited.

## Tooling Status

No language workspace, package manager, build system, dependency version, or task runner has been selected. Their future configuration files must be introduced only after an evidence-backed technology decision in [`.ai/techstack.md`](.ai/techstack.md) and any required ADR.

## Adding a Workspace Member

Before adding an application or package:

1. Define its responsibility, owner, public interface, allowed dependencies, tests, and documentation.
2. Follow [`.ai/architecture_decision_flow.md`](.ai/architecture_decision_flow.md).
3. Add a README and update the package contract and architecture references.
4. Avoid placeholder source code and speculative dependency declarations.

