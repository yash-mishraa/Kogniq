# Kogniq Glossary

This file is the single source of truth for repository terminology. Definitions describe intended concepts, not implemented types or services. Conceptual data objects are detailed in [`data_dictionary.md`](data_dictionary.md).

## Learning and Product Terms

### Learning Domain

- **Definition:** A bounded body of curriculum, terminology, assessment rules, and learning policies integrated with Kogniq through a future domain contract.
- **Purpose:** Isolate examination-specific knowledge from the reusable platform core.
- **Examples:** GATE as the first planned reference domain; GRE or CAT as possible future domains.
- **Related Terms:** Curriculum, Plugin, Module, Knowledge Concept.
- **Notes:** A named future domain is not evidence of implemented support.

### Knowledge Concept

- **Definition:** A uniquely identifiable unit of knowledge or skill that a learner can study, demonstrate, and relate to other concepts.
- **Purpose:** Provide the common unit for content mapping, assessment, knowledge tracing, and recommendation.
- **Examples:** Matrix rank; reading inference; probability.
- **Related Terms:** Topic, Curriculum, Knowledge State, Graph Node.
- **Notes:** Concept granularity is domain-owned and must be versioned.

### Assessment Item

- **Definition:** A single gradable prompt or task intended to elicit evidence about one or more knowledge concepts.
- **Purpose:** Measure learner performance and produce interpretable learning evidence.
- **Examples:** Multiple-choice question; numerical-answer problem; short response.
- **Related Terms:** Assessment, Question, Question Attempt, Knowledge Trace.
- **Notes:** Scoring rules and validity may differ by learning domain.

### Student Model

- **Definition:** The governed representation of a learner's relevant state, history, preferences, and inferred learning needs.
- **Purpose:** Support personalization without treating raw activity as complete knowledge.
- **Examples:** Concept mastery estimates, confidence, recent practice, stated goals.
- **Related Terms:** Knowledge State, Knowledge Trace, Recommendation.
- **Notes:** Inferences must be distinguishable from user-provided facts and respect privacy rules.

### Knowledge Trace

- **Definition:** A time-ordered record of learning evidence and resulting knowledge-state estimates.
- **Purpose:** Explain how estimated understanding changes over time.
- **Examples:** Attempts and revisions associated with a concept across several sessions.
- **Related Terms:** Student Model, Knowledge State, Question Attempt, Study Session.
- **Notes:** A trace includes uncertainty; it is not a transcript of a learner's mind.

### Knowledge State

- **Definition:** A point-in-time estimate of a learner's understanding of one or more knowledge concepts.
- **Purpose:** Inform appropriate practice, revision, and explanation choices.
- **Examples:** Emerging, developing, or proficient with an associated confidence estimate.
- **Related Terms:** Knowledge Trace, Student Model, Knowledge Concept.
- **Notes:** State labels and scales require validation and must not imply unwarranted certainty.

### Learning Artifact

- **Definition:** A governed resource used or produced during learning.
- **Purpose:** Give lessons, notes, documents, questions, explanations, and practice material a shared conceptual category.
- **Examples:** Uploaded notes, worked solution, syllabus document, generated summary.
- **Related Terms:** Document, Flashcard, Assessment Item, Citation.
- **Notes:** Provenance, ownership, and generated status must remain visible.

### Study Session

- **Definition:** A bounded period of learner activity directed toward one or more learning goals.
- **Purpose:** Group events and outcomes for continuity, analytics, and planning.
- **Examples:** A 30-minute revision block; a mock-test review.
- **Related Terms:** Revision Plan, Knowledge Trace, Learning Artifact.
- **Notes:** Product sessions and authentication sessions are different concepts.

### Revision Plan

- **Definition:** An ordered, time-aware set of recommended revision tasks tied to learner goals and evidence.
- **Purpose:** Turn knowledge-state signals into actionable study work.
- **Examples:** Revisit weak concepts this week; complete spaced flashcard reviews.
- **Related Terms:** Revision Task, Recommendation, Planner Agent, Knowledge State.
- **Notes:** A plan is advisory and must expose rationale and allow learner control.

### Flashcard

- **Definition:** A compact recall artifact with a prompt side and an answer or explanation side.
- **Purpose:** Support active recall and spaced revision.
- **Examples:** Definition-to-term card; formula recall card.
- **Related Terms:** Learning Artifact, Revision Task, Knowledge Concept.
- **Notes:** Generated cards require provenance and quality checks.

### Curriculum

- **Definition:** A versioned organization of expected concepts, skills, scopes, and relationships for a learning domain.
- **Purpose:** Anchor content, assessment, progress, and recommendations to an explicit learning target.
- **Examples:** A published examination syllabus mapped to concepts and topics.
- **Related Terms:** Learning Domain, Topic, Knowledge Concept, Knowledge Graph.
- **Notes:** Curriculum versions must not be silently combined.

## Retrieval and Generation Terms

### Embedding

- **Definition:** A numeric vector representation used to compare semantic or structural similarity.
- **Purpose:** Support retrieval, clustering, ranking, or analysis.
- **Examples:** A vector representing a document chunk or question.
- **Related Terms:** Chunk, Retriever, Vector Store, Inference.
- **Notes:** Model identity, version, dimensionality, and source object are essential metadata.

### Chunk

- **Definition:** A bounded segment derived from a source document for retrieval or processing.
- **Purpose:** Make large artifacts addressable while preserving source context.
- **Examples:** A paragraph group, section, or table with positional metadata.
- **Related Terms:** Document, Embedding, Citation, Retriever Pipeline.
- **Notes:** A chunk is derived data and must retain provenance to its source.

### Retriever

- **Definition:** A component that selects candidate evidence relevant to a query.
- **Purpose:** Find grounded context before ranking or generation.
- **Examples:** Semantic retrieval; keyword retrieval; graph-based retrieval.
- **Related Terms:** Retriever Pipeline, Vector Store, Chunk.
- **Notes:** Retrieval quality is evaluated independently from generation quality.

### Retriever Pipeline

- **Definition:** The ordered retrieval process from query preparation through candidate selection, filtering, and reranking.
- **Purpose:** Produce relevant, permitted, and traceable context for downstream use.
- **Examples:** Rewrite query, search indexes, filter by domain, rerank results.
- **Related Terms:** Retriever, Pipeline, Generator, Citation.
- **Notes:** Each stage must expose measurable behavior and failure semantics.

### Generator

- **Definition:** A model-backed component that produces language or structured output from instructions and context.
- **Purpose:** Create explanations, answers, plans, or transformations grounded in available evidence.
- **Examples:** Producing a cited explanation from retrieved curriculum material.
- **Related Terms:** Inference, Retriever Pipeline, Citation, Teacher Agent.
- **Notes:** A generator is not a source of truth and must not fabricate evidence.

### Vector Store

- **Definition:** A system or logical capability that stores vectors and supports similarity-based lookup.
- **Purpose:** Make embedded objects searchable.
- **Examples:** A collection of chunk embeddings filtered by domain and curriculum version.
- **Related Terms:** Embedding, Retriever, Chunk.
- **Notes:** No product or vendor has been selected.

### Citation

- **Definition:** A traceable reference connecting a claim or output span to supporting source material.
- **Purpose:** Enable verification, attribution, and provenance.
- **Examples:** A reference to a document section and source location.
- **Related Terms:** Document, Chunk, Generator, Learning Artifact.
- **Notes:** A citation proves source linkage, not that the claim is correct.

## Agent Terms

### Teacher Agent

- **Definition:** A future bounded agent role that selects instructional actions and explanations within approved learning and safety policies.
- **Purpose:** Adapt teaching behavior to a learner's goal and evidence.
- **Examples:** Choosing a hint before a full solution; checking understanding.
- **Related Terms:** Planner Agent, Student Model, Generator.
- **Notes:** This role is planned only and may not bypass domain services or evidence requirements.

### Planner Agent

- **Definition:** A future bounded agent role that proposes and revises multi-step study plans using approved tools and constraints.
- **Purpose:** Coordinate goals, available time, prerequisites, and revision needs.
- **Examples:** Drafting a weekly revision sequence.
- **Related Terms:** Revision Plan, Teacher Agent, Recommendation.
- **Notes:** Plans remain user-controllable and agent actions must be auditable.

## Knowledge Graph Terms

### Knowledge Graph

- **Definition:** A versioned network of learning entities and typed relationships.
- **Purpose:** Represent prerequisites, composition, alignment, and other relationships that are difficult to express as flat lists.
- **Examples:** A concept prerequisite graph for a curriculum.
- **Related Terms:** Graph Node, Graph Edge, Curriculum, Knowledge Concept.
- **Notes:** Core graph contracts must support domain-specific extensions without merging domain identities.

### Graph Node

- **Definition:** An identifiable entity represented as a vertex in a knowledge graph.
- **Purpose:** Provide an endpoint for typed relationships.
- **Examples:** Concept, topic, curriculum unit, or learning artifact.
- **Related Terms:** Graph Edge, Knowledge Graph, Knowledge Concept.
- **Notes:** Node type, namespace, version, and provenance are required conceptual metadata.

### Graph Edge

- **Definition:** A typed, directed or undirected relationship between graph nodes.
- **Purpose:** Encode meaning such as prerequisite, part-of, assesses, or related-to.
- **Examples:** Calculus `prerequisite_of` differential equations.
- **Related Terms:** Graph Node, Knowledge Graph.
- **Notes:** Direction, evidence, validity interval, and domain scope must be explicit.

## Evaluation and ML Terms

### Evaluation Dataset

- **Definition:** A versioned, governed collection of examples and expected observations used to measure system behavior.
- **Purpose:** Support comparable quality, safety, retrieval, model, and product evaluations.
- **Examples:** Expert-reviewed question-answer pairs with citation expectations.
- **Related Terms:** Evaluation Result, Experiment, Dataset.
- **Notes:** Evaluation data must be separated from training data where leakage would invalidate results.

### Experiment

- **Definition:** A reproducible investigation with a stated hypothesis, controlled variables, measures, and conclusion.
- **Purpose:** Reduce uncertainty before adopting a model, method, or product behavior.
- **Examples:** Comparing two retrieval strategies on the same evaluation dataset.
- **Related Terms:** Evaluation Dataset, Model, Inference.
- **Notes:** An experiment is not production functionality.

### Inference

- **Definition:** Execution of a trained or configured model to produce a prediction, score, representation, or generated output.
- **Purpose:** Apply model behavior to an input.
- **Examples:** Estimating knowledge state; generating an embedding.
- **Related Terms:** Model, Embedding, Generator, Pipeline.
- **Notes:** Inference inputs, model version, outputs, latency, and failures must be observable.

### Pipeline

- **Definition:** An ordered, observable sequence of processing stages with explicit inputs and outputs.
- **Purpose:** Make multi-step work reproducible and independently testable.
- **Examples:** Ingestion pipeline; retrieval pipeline; evaluation pipeline.
- **Related Terms:** Retriever Pipeline, Inference, Experiment.
- **Notes:** A pipeline may run synchronously or asynchronously; the term does not imply a technology.

## Repository Governance Terms

### Plugin

- **Definition:** A separately owned extension that conforms to a versioned platform contract without changing the platform core.
- **Purpose:** Add bounded capability or domain behavior while preserving reuse and isolation.
- **Examples:** The future GATE learning-domain reference plugin.
- **Related Terms:** Learning Domain, Module, Feature.
- **Notes:** Discovery, packaging, isolation, and compatibility mechanisms remain undecided.

### Module

- **Definition:** A cohesive unit of source, documentation, and ownership behind a defined public boundary.
- **Purpose:** Organize responsibilities and control dependencies.
- **Examples:** Retrieval evaluation module; curriculum mapping module.
- **Related Terms:** Plugin, Feature, Service Boundary.
- **Notes:** A module is not necessarily a deployable service.

### Feature

- **Definition:** A coherent product behavior that creates an observable user or operator outcome.
- **Purpose:** Express product scope independently of implementation shape.
- **Examples:** Review cited explanations; receive a revision recommendation.
- **Related Terms:** Functional Requirement, Module, Milestone.
- **Notes:** A feature may span modules and requires acceptance criteria.

### Milestone

- **Definition:** A roadmap outcome with dependencies, status, and completion criteria.
- **Purpose:** Organize delivery around verified outcomes rather than activity.
- **Examples:** Stage 0 repository planning completion.
- **Related Terms:** Repository Stage, Feature, Roadmap.
- **Notes:** A milestone does not prescribe implementation.

### ADR

- **Definition:** Architecture Decision Record: an immutable account of a durable decision, context, alternatives, and consequences.
- **Purpose:** Preserve why significant choices were made.
- **Examples:** ADR-0002, Repository Rebranding to Kogniq.
- **Related Terms:** Architecture Decision Flow, Session, Milestone.
- **Notes:** Accepted ADRs remain in history when superseded.

### Repository Stage

- **Definition:** A bounded roadmap phase representing the repository's current maturity and authorized class of work.
- **Purpose:** Prevent premature implementation and make dependencies explicit.
- **Examples:** Stage 0 Repository Planning; Stage 1 Infrastructure Foundations.
- **Related Terms:** Milestone, Prompt, Session.
- **Notes:** Stage changes require explicit direction and updated progress.

### Prompt

- **Definition:** A scoped instruction set authorizing work within a session.
- **Purpose:** Define requested outcomes, constraints, and stop conditions.
- **Examples:** Stage 0.5 Prompt 1, Repository Intelligence Layer.
- **Related Terms:** Session, Repository Stage, Prompt Archive.
- **Notes:** A prompt does not override higher-priority repository decisions without explicitly resolving the conflict.

### Session

- **Definition:** A continuous unit of repository work performed by a human or AI contributor under a defined prompt.
- **Purpose:** Bound changes and preserve a reviewable handoff.
- **Examples:** A documentation-only session ending with a progress entry.
- **Related Terms:** Prompt, Repository Stage, ADR.
- **Notes:** Every session follows the startup and end sequences in [`handoff.md`](handoff.md).

