# Shared Package

## Purpose

Reserve a small, stable home for primitives and contracts genuinely shared across Kogniq boundaries.

## Responsibilities

Own framework-neutral configuration contracts, standard-library logging setup, generic exception semantics, foundational interfaces, constants, and narrowly reusable utilities.

## Public Interface

Exports from `shared.config`, `shared.logging`, `shared.exceptions`, and `shared.interfaces` are public and require compatibility review. Internal implementation files remain private.

## Dependencies

Remains independent of all other Kogniq packages and applications and currently uses only the Python standard library. Future third-party dependencies require exceptional justification.

## Future Expansion

Add primitives only after at least two owning boundaries need the same stable semantic contract. Prefer an owning package when responsibility is specific.

## Ownership

Architecture/platform maintainers — `<OWNER_NAME>`.

## What Does NOT Belong Here

Business rules, domain-specific types, provider SDKs, storage clients, framework integrations, convenience dumping grounds, or mutable global state.
