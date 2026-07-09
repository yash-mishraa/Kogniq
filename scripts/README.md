# Scripts

## Purpose

Future home of narrow repository-wide operational utilities.

## Future Responsibilities

Repeatable setup, validation, maintenance, migration support, and developer automation that does not belong to one module.

Reserved categories:

- `development/` for local engineering and validation helpers.
- `deployment/` for future controlled release helpers.
- `maintenance/` for bounded repository and data maintenance.
- `evaluation/` for reproducible evaluation entry points.

These directories currently contain documentation only.

## Ownership

Platform engineering — Yash Mishra.

## What Belongs Here

Documented, idempotent where practical, non-interactive utilities with clear inputs, outputs, failure behavior, and tests when warranted.

## What Should Not Belong Here

Core business logic, hidden production services, credentials, destructive defaults, one-off personal scripts, or module-specific logic.
