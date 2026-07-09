# Conceptual Data Dictionary

This document defines important product data objects without prescribing schemas, storage, identifiers, or APIs. Field lists are possibilities, not implementation contracts. Terms follow [`glossary.md`](glossary.md); privacy and sizing assumptions follow [`system_constraints.md`](system_constraints.md).

## User

- **Description:** A person who interacts with Kogniq in a learner, reviewer, evaluator, or operator capacity.
- **Purpose:** Associate authorized preferences, goals, activity, and responsibilities with a person.
- **Relationships:** Owns Study Sessions and Question Attempts; may review Documents or Evaluation Results.
- **Possible Fields:** Identifier, roles, locale, accessibility preferences, consent status, created time.
- **Lifecycle:** Created with consent; updated by authorized actions; exported, deactivated, or deleted under policy.
- **Owner:** Identity and privacy capability owner — `<OWNER_NAME>`.
- **Future Extensions:** Institutional membership, guardian relationship, pseudonymous research participation.

## Study Session

- **Description:** A bounded period of learning activity.
- **Purpose:** Group goals, artifacts, attempts, and outcomes for continuity and analysis.
- **Relationships:** Belongs to a User and Domain; contains Question Attempts and artifact interactions.
- **Possible Fields:** Identifier, user reference, domain reference, goals, start/end times, status, summary.
- **Lifecycle:** Started, active, completed or abandoned, retained or deleted under learner-data policy.
- **Owner:** Learning workflow owner — `<OWNER_NAME>`.
- **Future Extensions:** Offline reconciliation, collaborative session, educator review.

## Assessment

- **Description:** A governed collection or sequence of assessment items with an evaluation purpose.
- **Purpose:** Diagnose, practice, benchmark, or verify learning.
- **Relationships:** Contains Questions; targets Concepts and a Curriculum; produces Question Attempts and results.
- **Possible Fields:** Identifier, domain, curriculum version, purpose, item references, timing policy, scoring policy, provenance.
- **Lifecycle:** Drafted, reviewed, published, versioned, retired.
- **Owner:** Domain assessment owner — `<OWNER_NAME>`.
- **Future Extensions:** Adaptive assembly, accommodations, alternate forms.

## Question

- **Description:** A gradable assessment item presented to a learner.
- **Purpose:** Elicit evidence about knowledge or skill.
- **Relationships:** Belongs to Assessments; maps to Concepts; has Question Attempts and source Documents.
- **Possible Fields:** Identifier, prompt, response format, options, answer specification, explanation, difficulty evidence, concept mappings, provenance.
- **Lifecycle:** Drafted, reviewed, published, versioned, corrected, retired.
- **Owner:** Domain content owner — `<OWNER_NAME>`.
- **Future Extensions:** Parameterized variants, multimedia, rubric-based responses.

## Question Attempt

- **Description:** A learner's response to a Question in a specific context.
- **Purpose:** Preserve assessment evidence and feedback history.
- **Relationships:** Belongs to a User, Question, and optionally Study Session or Assessment; informs Knowledge State.
- **Possible Fields:** Identifier, response, timestamps, score, feedback, hint use, confidence, context and version references.
- **Lifecycle:** Started, submitted, evaluated, optionally reviewed or invalidated, retained under privacy policy.
- **Owner:** Assessment workflow owner — `<OWNER_NAME>`.
- **Future Extensions:** Partial-credit trace, manual review, offline synchronization.

## Concept

- **Description:** A domain-scoped unit of knowledge or skill.
- **Purpose:** Align curricula, artifacts, questions, learner evidence, and recommendations.
- **Relationships:** Belongs to a Domain and Curriculum version; grouped by Topics; represented by graph nodes and edges.
- **Possible Fields:** Identifier, namespace, name, definition, scope, aliases, domain, version, provenance.
- **Lifecycle:** Proposed, reviewed, published, versioned, merged or retired with migration guidance.
- **Owner:** Knowledge engineering and domain reviewer — `<OWNER_NAME>`.
- **Future Extensions:** Multilingual labels, competency levels, cross-domain equivalence.

## Topic

- **Description:** A domain-owned grouping of related Concepts.
- **Purpose:** Provide curriculum navigation and reporting above concept granularity.
- **Relationships:** Contains or references Concepts; belongs to a Curriculum; may nest under other Topics.
- **Possible Fields:** Identifier, name, description, parent reference, ordering, domain, curriculum version.
- **Lifecycle:** Curated, versioned, reorganized, retired.
- **Owner:** Domain curriculum owner — `<OWNER_NAME>`.
- **Future Extensions:** Multiple taxonomies, user-defined views.

## Domain

- **Description:** Metadata describing an available learning-domain plugin and its governed scope.
- **Purpose:** Isolate domain identity, compatibility, curriculum, and ownership.
- **Relationships:** Owns Curricula, Concepts, Questions, Documents, and domain-specific evaluations.
- **Possible Fields:** Stable key, display name, version, contract version, status, owner, supported locales, policy references.
- **Lifecycle:** Proposed, reviewed, installed, enabled, upgraded, disabled, retired.
- **Owner:** Domain governance owner — `<OWNER_NAME>`.
- **Future Extensions:** External certification, tenant-specific domains, compatibility ranges.

## Embedding

- **Description:** A vector representation derived from another governed object.
- **Purpose:** Enable similarity search, ranking, or analysis.
- **Relationships:** Represents a Chunk, Document, Question, Concept, or other eligible object; produced by a Model.
- **Possible Fields:** Source reference and version, vector, model reference, dimensions, creation time, normalization and access metadata.
- **Lifecycle:** Generated, indexed, invalidated when source or model changes, deleted with governed source where required.
- **Owner:** Retrieval or ML owner — `<OWNER_NAME>`.
- **Future Extensions:** Multimodal vectors, quantization, multiple representation spaces.

## Chunk

- **Description:** A derived, addressable segment of a Document.
- **Purpose:** Support retrieval while retaining source location and context.
- **Relationships:** Belongs to a Document; may have Embeddings and be referenced by Citations.
- **Possible Fields:** Identifier, document version, content, sequence, structural path, offsets, token estimate, metadata, derivation version.
- **Lifecycle:** Derived, validated, indexed, regenerated on source or policy change, deleted with source.
- **Owner:** Retrieval ingestion owner — `<OWNER_NAME>`.
- **Future Extensions:** Hierarchical chunks, table-aware segments, multimodal regions.

## Citation

- **Description:** A link from a claim or output to supporting source material.
- **Purpose:** Preserve verification and attribution.
- **Relationships:** References a Document or Chunk; attaches to generated output, feedback, or Learning Artifact.
- **Possible Fields:** Identifier, source reference and version, locator, quoted span or claim span, access time, attribution.
- **Lifecycle:** Created with output, validated, invalidated if source access or version changes, retained with the dependent record.
- **Owner:** Grounding and provenance owner — `<OWNER_NAME>`.
- **Future Extensions:** Entailment score, reviewer status, citation graph.

## Recommendation

- **Description:** A ranked, explainable suggestion for a learner action or resource.
- **Purpose:** Convert goals and evidence into useful next choices.
- **Relationships:** Belongs to a User and Domain; may reference Knowledge States, Concepts, Revision Tasks, or Learning Artifacts.
- **Possible Fields:** Identifier, recommendation type, target, rationale, evidence references, rank, confidence, model or rule version, status.
- **Lifecycle:** Generated, presented, accepted, dismissed, completed, expired, or invalidated.
- **Owner:** Personalization owner — `<OWNER_NAME>`.
- **Future Extensions:** Counterfactual rationale, educator approval, group recommendations.

## Revision Task

- **Description:** A concrete, schedulable learning action within a revision plan.
- **Purpose:** Make recommendations actionable and trackable.
- **Relationships:** Belongs to a User and Revision Plan; targets Concepts and may reference Questions, Flashcards, or Documents.
- **Possible Fields:** Identifier, task type, target references, planned time, estimated duration, rationale, priority, status, completion evidence.
- **Lifecycle:** Proposed, accepted, scheduled, rescheduled, completed, skipped, expired.
- **Owner:** Planning capability owner — `<OWNER_NAME>`.
- **Future Extensions:** Recurrence, reminders, calendar integration, collaborative assignment.

## Knowledge Graph Node

- **Description:** A versioned entity represented in a knowledge graph.
- **Purpose:** Serve as an endpoint for typed learning relationships.
- **Relationships:** May represent a Concept, Topic, Curriculum unit, or Learning Artifact; connected by Knowledge Graph Edges.
- **Possible Fields:** Stable identifier, namespace, node type, entity reference, labels, domain, version, provenance.
- **Lifecycle:** Proposed, validated, published, versioned, deprecated, removed with migration.
- **Owner:** Knowledge graph owner — `<OWNER_NAME>`.
- **Future Extensions:** External identifiers, multilingual properties, temporal validity.

## Knowledge Graph Edge

- **Description:** A typed relationship between two Knowledge Graph Nodes.
- **Purpose:** Express prerequisite, containment, alignment, assessment, or semantic relationships.
- **Relationships:** Connects source and target nodes; may cite evidence Documents.
- **Possible Fields:** Identifier, source, target, relationship type, direction, weight or confidence, domain, evidence, validity, version.
- **Lifecycle:** Proposed, reviewed, published, revised, deprecated, removed.
- **Owner:** Knowledge graph owner with domain reviewer — `<OWNER_NAME>`.
- **Future Extensions:** Competing claims, reviewer consensus, inferred-edge provenance.

## Experiment

- **Description:** A versioned record of a reproducible investigation.
- **Purpose:** Track hypothesis, configuration, evidence, and conclusion before adoption.
- **Relationships:** Uses Datasets and Models; produces Evaluation Results and artifacts.
- **Possible Fields:** Identifier, hypothesis, owner, configuration, input versions, code revision, start/end times, status, conclusion.
- **Lifecycle:** Planned, running, completed, failed, reviewed, archived.
- **Owner:** Conducting research or engineering owner — `<OWNER_NAME>`.
- **Future Extensions:** Approval gates, cost and carbon accounting, lineage graphs.

## Model

- **Description:** A versioned computational artifact or external model configuration used for inference.
- **Purpose:** Identify the behavior-producing asset behind predictions, vectors, rankings, or generation.
- **Relationships:** Produces Embeddings or outputs; used by Experiments; measured by Evaluation Results.
- **Possible Fields:** Identifier, task, version, provider or artifact reference, training-data declaration, configuration, limitations, status.
- **Lifecycle:** Proposed, evaluated, approved, deployed, monitored, deprecated, retired.
- **Owner:** ML/model governance owner — `<OWNER_NAME>`.
- **Future Extensions:** Fine-tuned lineage, safety card, regional deployment variants.

## Evaluation Result

- **Description:** A versioned set of measurements and findings from an evaluation run.
- **Purpose:** Support quality comparison, regression detection, and release decisions.
- **Relationships:** Evaluates a Model, pipeline, Feature, or Experiment against an Evaluation Dataset.
- **Possible Fields:** Identifier, subject and version, dataset version, configuration, metrics, slices, threshold outcomes, errors, reviewer, time.
- **Lifecycle:** Produced, validated, reviewed, accepted or rejected for a decision, retained for comparison.
- **Owner:** Evaluation owner — `<OWNER_NAME>`.
- **Future Extensions:** Statistical confidence, human-review adjudication, continuous monitoring link.

## Document

- **Description:** A governed source artifact containing learning or operational content.
- **Purpose:** Preserve content, provenance, rights, versions, and processing status.
- **Relationships:** Belongs to a Domain or repository scope; produces Chunks; supports Citations, Questions, and Concepts.
- **Possible Fields:** Identifier, title, source, owner, license, content type, language, checksum, version, access classification, ingestion status.
- **Lifecycle:** Acquired, rights-checked, validated, processed, published, revised, restricted, retired, deleted.
- **Owner:** Data and content governance owner — `<OWNER_NAME>`.
- **Future Extensions:** Multimedia transcripts, redaction history, external synchronization.

## Flashcard

- **Description:** A compact learning artifact pairing a recall prompt with an answer or explanation.
- **Purpose:** Support active recall and spaced revision.
- **Relationships:** Maps to Concepts and source Documents; may appear in Revision Tasks and Study Sessions.
- **Possible Fields:** Identifier, front, back, concept mappings, citations, author or generator version, difficulty, review status.
- **Lifecycle:** Drafted or generated, reviewed, published, practiced, revised, retired.
- **Owner:** Learning content owner — `<OWNER_NAME>`.
- **Future Extensions:** Cloze deletion, multimedia, learner-authored variants, scheduling metadata.

