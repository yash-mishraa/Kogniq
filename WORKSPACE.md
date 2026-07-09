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

The Python workspace uses `uv`, targets Python 3.12–3.13, and centralizes Ruff, MyPy, pytest, and coverage configuration in `pyproject.toml`. The root project is non-packaged; documentation-only directories become uv workspace members only when they gain an approved Python distribution boundary. No frontend workspace, application framework, or runtime service dependency is selected.

## Adding a Workspace Member

Before adding an application or package:

1. Define its responsibility, owner, public interface, allowed dependencies, tests, and documentation.
2. Follow [`.ai/architecture_decision_flow.md`](.ai/architecture_decision_flow.md).
3. Add a README and update the package contract and architecture references.
4. Avoid placeholder source code and speculative dependency declarations.
