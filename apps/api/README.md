# API Application

## Purpose

Future composition root for Kogniq's authoritative application workflows and external service contracts.

## Responsibilities

Validate requests, integrate identity and authorization, orchestrate public package capabilities, define transaction and idempotency boundaries, and translate failures at the application edge.

## Public Interface

Only reviewed, versioned application commands, queries, events, and future external contracts. The current API inventory is planning-only in [`.ai/api_catalog.md`](../../.ai/api_catalog.md).

## Dependencies

May depend on `packages/shared` and approved public interfaces from capability and domain packages. It must follow [the package contract](../../.ai/package_contracts.md#appsapi).

## Future Expansion

Composition modules may later cover learning sessions, documents, assessments, recommendations, revision, and domain discovery after their roadmap stages are authorized.

## Ownership

Backend/platform team — `<OWNER_NAME>`.

## What Does NOT Belong Here

Frontend code, reusable domain rules, package internals, direct cross-package storage access, provider-specific business logic, experiments, secrets, or framework scaffolding before selection.

