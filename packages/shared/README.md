# Shared Package (`packages/shared`)

## Purpose
The `shared` package is the foundational layer of Kogniq. It contains generic domain primitives, abstract interfaces, and core types that are used universally across the entire monorepo.

## Responsibilities

### What belongs here
- Base domain models (`Entity`, `ValueObject`, `DomainEvent`).
- Cross-cutting concerns (e.g., timestamps, global exception bases).
- Universal enums and configuration objects.

### What does NOT belong here
- Business logic tied to a specific domain (e.g., Chunking, Learning).
- Any concrete implementation of a database or LLM provider.
- Orchestration logic.

## Public API
- `shared.domain.entity.Entity`: Base class for mutable domain entities.
- `shared.domain.value_object.ValueObject`: Base class for immutable value objects.
- `shared.domain.events.DomainEvent`: Base for domain events.
- `shared.exceptions.KogniqError`: Global exception base.

## Architecture
This package sits at the very bottom of the dependency graph. It has no dependencies on any other package in Kogniq. All other packages depend on it.

## Dependencies
- None (pure Python, standard library).

## Relationships
- Inherited by: `content`, `embedding`, `retrieval`, `knowledge`, `pipeline`, `learning-content`.

## Current Features
- Fully implemented base abstractions.
- Immutable data structures utilizing `dataclasses`.
- Strict typing and custom validators.

## Planned Features
- Event bus abstractions for decoupled domain communication.
- Enhanced telemetry and logging traits.

## Examples
*No runnable developer demos exist for this foundational package.*

## Quality Gates
- **Tests**: `uv run python -m pytest packages/shared/tests/`
- **MyPy**: `uv run python -m mypy packages/shared/`
- **Ruff**: `uv run ruff check packages/shared/`
