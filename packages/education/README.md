# Education Domain (`kogniq-education`)

The `education` package models the human element of Kogniq. It focuses on the pedagogy, the student's journey, and the active tutoring sessions.

## Responsibilities

- **Student Modeling**: Tracking progress, retention, and mastery of concepts.
- **Tutoring Sessions**: Managing the state of a conversation between an AI tutor and a student.
- **Assessments**: Generating quizzes and evaluating student responses.

## What Belongs Inside

- Domain entities for `Student`, `TutorSession`, `Assessment`, and `ProgressRecord`.
- Business rules for mastery thresholds (e.g., "A student must score 80% to master a concept").
- Learning path generation algorithms.

## What Does NOT Belong Inside

- Curriculum definitions (that is the `learning` package).
- The raw source documents (that is the `content` package).
- Direct LLM HTTP requests (that belongs in an infrastructure or application layer).

## Public API

- `Student`, `TutorSession`, `Interaction` models.
- `MasteryLevel` and `ConfidenceScore` value objects.

## Internal Architecture

The education domain is the highest level of the core business logic. It brings together a `Student` and a `Concept` (from `learning`) via a `TutorSession` that references a `ChunkCollection` (from `content`).

## Design Principles

- **State Encapsulation**: A `TutorSession` manages its own internal interaction history.
- **Immutability of History**: Past interactions and assessment scores cannot be modified.

## Current Status

**Foundations Implemented**. Base models and value objects are established.

## Future Work

- Integration with Multi-Agent Systems for active conversational tutoring.
- RAG (Retrieval-Augmented Generation) infrastructure for providing agents with educational context.
