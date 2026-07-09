# Domain Package

## Purpose

Contain Kogniq's examination-neutral business language and bounded contexts.

## Responsibilities

Own core learning invariants and contracts across learning, assessment, student, documents, analytics, and recommendation contexts while preserving clear context boundaries.

## Public Interface

Future context-level use cases, entities, value semantics, domain events, and ports. No interface or model is implemented in this stage.

## Dependencies

May depend only on stable, framework-neutral contracts from `packages/shared`. Bounded contexts communicate through explicit contracts, not private imports.

## Future Expansion

Context boundaries may gain application ports and domain services after requirements and ubiquitous language are validated. Learning-domain plugins will extend approved contracts rather than modify this core.

## Ownership

Domain architecture and affected capability owners — `<OWNER_NAME>`.

## What Does NOT Belong Here

HTTP, UI, database or ORM concerns, provider SDKs, deployment configuration, model inference, examination-specific branching, or cross-context shortcuts.

