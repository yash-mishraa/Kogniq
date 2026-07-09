# Product Requirements

This document describes intended product behavior. It does not select technologies, define APIs, or authorize implementation. Terms follow [`glossary.md`](glossary.md); constraints follow [`system_constraints.md`](system_constraints.md).

## Vision

Kogniq is an AI Learning Intelligence Platform that helps learners understand what to study, learn with grounded assistance, practice deliberately, and revise based on evidence. Its reusable core supports multiple competitive-examination domains through isolated domain plugins. GATE is the first planned reference domain.

## Target Users

- Independent learners preparing for structured, high-stakes examinations.
- Learners who need help diagnosing gaps and planning limited study time.
- Educators and subject experts who curate learning knowledge and evaluate quality.
- Researchers and engineers who assess learning-intelligence methods.
- Platform operators responsible for safety, quality, privacy, and reliability.

## User Personas

### Goal-Driven Learner

Has a target examination and date, wants a realistic plan, and needs progress expressed against a curriculum rather than raw activity.

### Gap-Focused Learner

Has studied previously but needs evidence-backed identification of weak concepts, targeted practice, and revision.

### Subject-Matter Reviewer

Validates curricula, relationships, questions, explanations, citations, and evaluation material for a specific learning domain.

### Platform Evaluator

Measures correctness, grounding, retrieval quality, personalization, safety, fairness, cost, and learning outcomes before release.

## Core User Journey

1. The learner selects an available learning domain and states a goal.
2. Kogniq establishes an initial view of curriculum scope and learner needs using transparent evidence.
3. The learner receives an editable study or revision plan with rationale.
4. The learner studies governed artifacts, asks questions, and completes assessments.
5. Kogniq returns grounded feedback with uncertainty and citations where applicable.
6. The learner's knowledge state is updated from relevant evidence.
7. Recommendations adapt while preserving learner control and visible reasoning.
8. Progress is reviewed against goals and curriculum, not engagement alone.

## Primary Features

These are planned product capabilities, not current functionality.

- Curriculum navigation and concept relationships.
- Goal setting and editable study planning.
- Grounded explanations with source citations.
- Concept-aligned assessments and feedback.
- Learner-controlled knowledge-state views.
- Evidence-based revision recommendations.
- Study-session continuity and progress review.
- Domain-aware learning behavior delivered through isolated plugins.
- Quality and safety evaluation visible to maintainers.

## Future Features

- Spaced revision and flashcard workflows.
- Multi-domain learner portfolios with explicit separation of domain state.
- Educator curation and review workflows.
- Bounded teacher and planner agents.
- Alternative learning-path comparison.
- Offline-capable study subsets.
- Multilingual learning experiences.
- Collaborative study and educator feedback, subject to privacy review.

## Out of Scope

- Guaranteeing examination results or replacing accredited instruction.
- Acting as an authoritative source without verifiable evidence.
- Generic open-ended chat unrelated to learning goals.
- Autonomous enrollment, payment, examination registration, or credential decisions.
- Covert surveillance, attention scoring, or manipulative engagement optimization.
- Diagnosing health, disability, or psychological conditions.
- Implementing every examination directly in the platform core.
- Any domain support not explicitly delivered and evaluated.

## Success Metrics

Targets must be approved before implementation; the categories below define what matters.

- **Learning effectiveness:** Improvement on held-out concept-aligned assessments and retention checks.
- **Grounding:** Supported-claim and citation-validity rates.
- **Recommendation quality:** Learner acceptance, completion, and measured benefit relative to baselines.
- **Calibration:** Agreement between confidence, knowledge-state estimates, and observed outcomes.
- **User agency:** Rate of understandable, editable, and reversible plans or recommendations.
- **Safety and privacy:** Confirmed policy violations, sensitive-data incidents, and successful deletion outcomes.
- **Reliability:** Successful completion of critical learning journeys and graceful degradation.
- **Accessibility:** Conformance results and task completion with assistive technology.
- **Efficiency:** User-perceived latency and cost per successful learning outcome.

Engagement time alone is not a success metric.

## Example Workflows

### Diagnose and Revise

A learner chooses a curriculum scope, completes a concept-aligned diagnostic, reviews uncertainty in the resulting knowledge state, accepts or edits a revision plan, and later checks retention.

### Ask for a Grounded Explanation

A learner asks a curriculum question. Kogniq retrieves permitted evidence, provides a level-appropriate explanation with citations, distinguishes uncertainty, and offers a check-for-understanding item.

### Review an Incorrect Attempt

A learner reviews an attempt, sees the applicable concept and reasoning error, requests a hint or worked explanation, and chooses whether the evidence should affect the current plan.

### Curate Domain Knowledge

A subject-matter reviewer examines a proposed concept, relationship, or artifact; checks provenance and curriculum version; and accepts, revises, or rejects it through an auditable workflow.

## Example Student Journey

A learner preparing through the future GATE reference domain selects a subject and target date. After a diagnostic, Kogniq indicates that two concepts need attention and explains the evidence and uncertainty. The learner shortens the proposed weekly plan to fit available time. During study, cited explanations link back to governed material. Later attempts improve the relevant knowledge estimates, and a retention check determines whether revision spacing should change. The journey demonstrates intended behavior only; GATE support is not implemented.

## Functional Requirements

- **FR-001:** The product shall identify the active learning domain and curriculum version in domain-scoped experiences.
- **FR-002:** The product shall keep learner records and recommendations correctly scoped across domains.
- **FR-003:** Learners shall be able to state, inspect, edit, and remove learning goals.
- **FR-004:** The product shall map governed learning artifacts and assessment items to identifiable concepts.
- **FR-005:** The product shall record relevant assessment evidence while preserving source and timing.
- **FR-006:** Knowledge-state estimates shall expose meaning, supporting evidence, uncertainty, and update time.
- **FR-007:** Plans and recommendations shall provide rationale and remain editable, dismissible, and reversible.
- **FR-008:** Grounded outputs shall identify supporting sources and distinguish unsupported or uncertain claims.
- **FR-009:** Learners shall be able to review study history and corrections relevant to their progress.
- **FR-010:** Subject reviewers shall be able to validate domain knowledge and provenance before approved use.
- **FR-011:** Evaluators shall be able to compare versioned system behavior against approved datasets and thresholds.
- **FR-012:** Users shall be able to request export and deletion of eligible personal learning data.
- **FR-013:** The product shall degrade safely when retrieval, model, graph, or recommendation capabilities are unavailable.
- **FR-014:** Domain-specific behavior shall be presented only for installed, compatible, and approved domains.

## Non Functional Requirements

- Product behavior shall be accessible, keyboard-operable, and understandable with assistive technology.
- Sensitive learner data shall be minimized, purpose-bound, protected, and auditable.
- Material recommendations and generated explanations shall be attributable to their inputs and system versions.
- Critical user actions shall have explicit failure states and safe recovery.
- Evaluation shall be reproducible across versioned domain, data, prompt, and model configurations.
- User-facing performance shall meet approved journey-specific targets defined before release.
- Domain plugins shall not weaken core privacy, safety, accessibility, or observability requirements.
- The product shall avoid deceptive certainty, hidden personalization, and dark patterns.

## Assumptions

- Initial users have intermittent or continuous web access; offline scope is undecided.
- Domain owners can provide legally usable curricula and subject expertise.
- Learning outcomes can be measured with imperfect but governed evidence.
- Users may have limited time, varied prior knowledge, and varied accessibility needs.
- Model and retrieval providers may change; product behavior cannot depend on one vendor identity.
- Authentication, payments, deployment regions, and business model remain outside this stage.

## Future Expansion

Kogniq may support additional competitive examinations, languages, curricula, educator workflows, and learning contexts through reviewed extensions. Expansion requires domain ownership, lawful content, evaluation datasets, compatibility checks, and evidence that core behavior remains reusable. Mentioned domains are examples, not commitments.

