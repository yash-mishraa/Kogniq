# Architecture Decision Flow

Use these flows to determine required documentation when a change has durable architectural impact. They complement the review checklists in [`coding_rules.md`](coding_rules.md); they do not replace maintainer judgment.

## Change Classification

```mermaid
flowchart TD
    A["Proposed repository change"] --> B{"Changes architecture, a public boundary, or a durable constraint?"}
    B -- "Yes" --> C["Update design.md"]
    C --> D["Create or supersede an ADR"]
    D --> E["Update affected reference documents"]
    E --> F["Append progress.md session"]
    B -- "No" --> G{"Changes product behavior or shared terminology?"}
    G -- "Product behavior" --> H["Update product_requirements.md"]
    G -- "Terminology" --> I["Update glossary.md and affected references"]
    G -- "Neither" --> J["Update local documentation if needed"]
    H --> F
    I --> F
    J --> F
```

An ADR is required for breaking changes, new platform boundaries, technology commitments, security or privacy posture changes, data-contract changes, domain-plugin contract changes, and intentional exceptions to dependency rules.

## Dependency Decision

```mermaid
flowchart TD
    A["Dependency proposed, replaced, or removed"] --> B["Update techstack.md status and rationale"]
    B --> C{"Major, cross-module, hard-to-reverse, or vendor-shaping?"}
    C -- "Yes" --> D["Create or supersede an ADR"]
    C -- "No" --> E["Record review rationale with the scoped change"]
    D --> F["Update design.md if boundaries or communication change"]
    E --> G["Validate license, security, maintenance, and lockfile impact"]
    F --> G
    G --> H["Append progress.md session"]
```

No dependency may be added merely because it is familiar. Selection evidence belongs in `techstack.md`; durable tradeoffs belong in an ADR.

## New Folder or Module

```mermaid
flowchart TD
    A["New folder or module proposed"] --> B["Confirm one clear responsibility and owner"]
    B --> C{"Existing boundary can own it?"}
    C -- "Yes" --> D["Place it within the owning boundary"]
    C -- "No" --> E["Update design.md directory responsibilities"]
    E --> F{"Creates a durable platform boundary?"}
    F -- "Yes" --> G["Create ADR"]
    F -- "No" --> H["Document rationale"]
    G --> I["Create README with ownership, contents, and exclusions"]
    H --> I
    D --> I
    I --> J["Update root navigation if top-level"]
    J --> K["Append progress.md session"]
```

Do not create empty organizational layers for hypothetical future code.

## Breaking Change

```mermaid
flowchart TD
    A["Breaking change identified"] --> B["ADR mandatory"]
    B --> C["Define affected contracts, users, data, plugins, and owners"]
    C --> D["Write migration and rollback notes"]
    D --> E["Update design.md and relevant requirements or dictionary"]
    E --> F["Define compatibility window and validation"]
    F --> G["Append progress.md session and link ADR"]
```

A breaking change includes incompatible behavior, data meaning, contract, plugin compatibility, security expectation, or removal of a supported workflow.

## Data and Terminology Changes

```mermaid
flowchart TD
    A["New or changed product concept"] --> B{"Shared term or conceptual entity?"}
    B -- "Shared term" --> C["Update glossary.md"]
    B -- "Conceptual entity" --> D["Update data_dictionary.md"]
    B -- "Both" --> E["Update both and cross-reference"]
    C --> F{"Changes product behavior or constraints?"}
    D --> F
    E --> F
    F -- "Behavior" --> G["Update product_requirements.md"]
    F -- "Constraint" --> H["Update system_constraints.md"]
    F -- "Neither" --> I["Review dependent documentation"]
    G --> J["Append progress.md session"]
    H --> J
    I --> J
```

Avoid defining the same term differently in local READMEs. Link to the glossary or data dictionary.

## Domain-Specific Change

```mermaid
flowchart TD
    A["Exam-specific behavior proposed"] --> B{"Fits an approved domain plugin contract?"}
    B -- "No contract exists" --> C["Stop implementation"]
    C --> D["Propose contract through design review and ADR"]
    B -- "Yes" --> E["Keep logic, data, prompts, and evaluation domain-scoped"]
    E --> F{"Requires platform-core modification?"}
    F -- "Yes" --> G["Demonstrate cross-domain need; architecture review and ADR"]
    F -- "No" --> H["Implement only within domain ownership"]
    D --> I["Update progress.md"]
    G --> I
    H --> I
```

The product identity rule in [`coding_rules.md`](coding_rules.md) is permanent: exam-specific convenience is not sufficient reason to change the platform core.

## Decision Completion Checklist

- The current architecture and accepted ADRs do not conflict.
- Owners and affected users are identified.
- Alternatives, reversibility, migration, and rollback are explicit.
- Product requirements, constraints, terminology, and data meaning remain aligned.
- Security, privacy, accessibility, evaluation, and domain isolation were reviewed.
- `progress.md` records the outcome without removing prior sessions.

