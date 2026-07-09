# Engineering Standards

These rules govern future implementation. Exceptions require a documented reason in review; architectural exceptions require an ADR.

## Project Identity Rule

- The product name is **Kogniq**.
- Learning domains such as GATE, GRE, CAT, and UPSC must never be hardcoded into core architecture.
- Domain-specific logic, data, prompts, terminology, and evaluation must remain modular and isolated.
- Core packages must be reusable across multiple learning domains.
- Examination-specific functionality must be implemented as a domain module or plugin against an approved contract, not by modifying the platform core.
- A proposed core change motivated by one examination requires evidence of a cross-domain platform need and review through [`architecture_decision_flow.md`](architecture_decision_flow.md).

## Folder Ownership

Every top-level module must have a named owner before implementation. Owners approve public contracts and dependency changes. Cross-module changes require review from each affected owner. Until delegated, ownership remains with Yash Mishra.

## Maximum File Size

Production source files should remain at or below 400 non-generated lines. Files exceeding 400 lines require a focused refactor or review justification. Generated files and declarative fixtures are exempt but must be identifiable.

## Maximum Function Size

Functions should remain at or below 50 logical lines and one level of abstraction. Exceptions require a clear reason and tests; complexity matters more than line-count gaming.

## Documentation Rules

- Document public contracts, invariants, side effects, failure modes, and non-obvious tradeoffs.
- Prefer rationale over narration of syntax.
- Update architecture, ADRs, and progress in the same change that alters them.
- Never claim planned behavior as implemented behavior.

## Typing Rules

Use the strictest practical compiler or checker settings. Public interfaces require explicit types. Avoid untyped escape hatches; isolate and justify unavoidable ones. Validate untrusted runtime input regardless of static types.

## Logging Rules

Use structured logs with severity, event name, and correlation context. Never log secrets, credentials, raw sensitive learner data, or unnecessary prompt content. Avoid duplicate logging across layers and do not use logs as control flow.

## Testing Expectations

Behavior changes require proportionate tests. Cover happy paths, boundaries, failures, permissions, and regressions. Public contracts require integration or contract tests. AI capabilities require deterministic fixtures, quality evaluations, and recorded thresholds; flaky tests are defects.

## Git Commit Conventions

Use focused commits with imperative Conventional Commit-style subjects, such as `docs: initialize architecture context`. Do not mix unrelated refactors and behavior changes. Reference relevant issues and ADRs; never commit secrets or large ungoverned artifacts.

## Dependency Rules

Use the fewest direct dependencies needed. Pin and lock versions according to ecosystem norms. Evaluate maintenance, license, security, size, and replacement cost. Centralize dependency declarations per workspace and prohibit circular module dependencies.

## Import Rules

Import through public module interfaces, not private paths. Keep imports explicit and ordered by language convention. Avoid wildcard imports and side-effect imports. Shared code must earn a stable home; do not create a generic dumping ground.

## Error Handling

Represent expected failures explicitly and preserve causal context. Translate errors at module boundaries, fail closed for security decisions, and avoid exposing internals to users. Retries require bounded attempts, backoff, idempotency analysis, and observability.

## Code Review Checklist

- Scope matches the issue or prompt and excludes unrelated work.
- Behavior, tests, and documentation agree.
- Inputs, errors, privacy, security, accessibility, and observability were considered.
- Naming and complexity make ownership clear.
- Dependencies and generated artifacts are justified.
- No secrets, sensitive data, or unsupported claims are introduced.

## Architecture Checklist

- Change respects directory ownership and service boundaries.
- Communication uses explicit public contracts.
- No circular dependency or private storage access is introduced.
- New technology or durable tradeoff has an ADR.
- Scaling, failure, security, data lifecycle, and rollback implications are understood.
- `.ai/design.md`, `.ai/progress.md`, and relevant decisions remain current.
- The Project Identity Rule is preserved and domain-specific behavior remains isolated.
