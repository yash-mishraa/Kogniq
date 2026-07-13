# Learning Domain (`kogniq-learning`)

The `learning` package models the theoretical structure of educational material. It does not care about the raw text of a PDF; instead, it cares about the *Concepts* and *Subjects* that the PDF teaches.

## Responsibilities

- **Curriculum Mapping**: Defining what concepts exist and how they group into subjects.
- **Prerequisite Validation**: Determining if Concept A must be learned before Concept B.
- **Knowledge Graphs**: Modeling the relational web of educational topics.

## What Belongs Inside

- Domain entities for `Subject`, `Concept`, and `LearningObjective`.
- Directed Acyclic Graph (DAG) logic for prerequisites.
- Validation rules for cyclic dependencies.

## What Does NOT Belong Inside

- Parsers for extracting concepts from text (that is an application service).
- The actual text of the learning materials (that is the `content` package).
- Student progress metrics (that is the `education` package).

## Public API

- `Subject`, `Concept`, `LearningObjective` models.
- `PrerequisiteValidator` for enforcing DAG integrity.

## Internal Architecture

The package relies heavily on immutable value objects (`ResourceHandle`) and rich domain entities that encapsulate their own validation logic.

## Design Principles

- **Fail Fast**: Invalid prerequisite graphs (e.g., cycles) raise exceptions immediately upon construction.
- **Pure Python**: No database dependencies. Graph relationships are modeled in memory.

## Current Status

**Foundations Implemented**. The core entities and prerequisite validators are complete.

## Future Work

- Integration with Knowledge Graph databases (e.g., Neo4j).
- Automated AI-driven concept extraction services.
