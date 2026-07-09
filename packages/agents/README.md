# Agents Package

## Purpose

Reserve the boundary for bounded, auditable agent workflows and approved tool orchestration.

## Responsibilities

Future agent roles, tool contracts, execution policies, state and memory rules, budgets, approvals, cancellation, recovery, safeguards, and evaluation hooks.

## Public Interface

Planned task, status, cancellation, approval, and execution-event contracts. No agent or tool is implemented.

## Dependencies

May depend on `packages/shared` and approved application tool contracts. Capability access must be mediated and least-privileged.

## Future Expansion

Teacher, planner, and reviewer agents may be introduced only where evaluation demonstrates value beyond deterministic workflows.

## Ownership

Agentic AI team with security review — `<OWNER_NAME>`.

## What Does NOT Belong Here

Unbounded autonomy, direct storage access, duplicated business rules, implicit network access, embedded credentials, examination-specific core logic, or authority bypasses.

