# Shared Package

## Purpose

Reserve a small, stable home for primitives and contracts genuinely shared across Kogniq boundaries.

## Responsibilities

In the future, own framework-neutral configuration contracts, logging contracts, exception semantics, interfaces, constants, and narrowly reusable utilities.

## Public Interface

Every eventual export is public and requires compatibility review. This stage contains documentation-only subdirectories and no exports.

## Dependencies

Must remain independent of all other Kogniq packages and applications. Future third-party dependencies require exceptional justification.

## Future Expansion

Add primitives only after at least two owning boundaries need the same stable semantic contract. Prefer an owning package when responsibility is specific.

## Ownership

Architecture/platform maintainers — `<OWNER_NAME>`.

## What Does NOT Belong Here

Business rules, domain-specific types, provider SDKs, storage clients, framework integrations, convenience dumping grounds, or mutable global state.

