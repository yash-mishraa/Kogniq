# System Constraints

This document records product-level assumptions and provisional engineering constraints. It does not select an implementation. Numeric values marked **Discovery Target** are planning hypotheses that must be validated and replaced by approved service-level objectives before production.

## Supported Platforms

- **Initial assumption:** Standards-based responsive web experience on desktop and mobile-class devices.
- Native desktop, mobile, browser-extension, and command-line clients are not committed.
- Server deployment platform and operating environment remain undecided.

## Performance Goals

- Keep core navigation and non-AI interactions responsive on representative mid-range hardware and constrained networks.
- Separate retrieval, inference, and orchestration measurements so slow stages are diagnosable.
- Prefer progressive feedback and graceful degradation for long-running work.
- Establish performance budgets per critical user journey before implementation.

## Latency Targets

Provisional discovery targets measured at the user-visible boundary:

| Interaction | Discovery Target | Notes |
| --- | --- | --- |
| Local UI feedback | within 100 ms | Perceived response to direct input where no network work is required |
| Standard data interaction | p95 within 1 second | Excludes long-running AI work |
| First useful feedback for generated response | p95 within 3 seconds | Streaming may be used; provider-independent target |
| Complete typical generated response | p95 within 15 seconds | Requires workload definition and quality guardrails |
| Background ingestion or evaluation | No fixed target | Must expose status, bounded retries, and completion expectations |

These are not SLOs and may change after representative measurement.

## Scalability Goals

- Scale interactive requests independently from ingestion, evaluation, and model workloads.
- Partition workload and data by learning domain where isolation or ownership requires it.
- Support asynchronous processing for tasks that need not block a learner.
- Avoid fixed user, document, or concept limits in core contracts.
- Do not adopt distributed deployment solely for hypothetical scale.

## Expected Dataset Sizes

No validated dataset inventory exists. Planning must cover:

- Small domain pilots with hundreds to thousands of governed artifacts.
- Mature domains with tens of thousands of concepts or assessment items and potentially millions of chunks or attempts.
- Evaluation datasets small enough for expert review but large enough for meaningful stratification.
- Growth models that distinguish source documents, derived chunks, embeddings, learner events, and evaluation artifacts.

Before storage selection, record representative distributions, retention, access patterns, update frequency, and legal constraints.

## Maximum Upload Sizes

- No upload capability or final maximum exists.
- **Discovery Target:** Evaluate a conservative per-file ceiling of 25 MiB for learner documents and separate administrator ingestion limits.
- Limits must also consider page count, extracted text, decompression, archive nesting, media duration, and processing cost.
- Reject unsupported or suspicious content before expensive processing and communicate the reason.

## Memory Assumptions

- **Client assumption:** Critical learning journeys should remain usable on devices with approximately 4 GiB total system memory; the product must not assume that memory is available exclusively to Kogniq.
- **Server assumption:** No memory tier is selected. Components must declare and measure representative working sets.
- Large datasets and models must not require complete in-memory loading unless explicitly justified.

## GPU Assumptions

- A GPU must not be required for ordinary client use.
- Server-side GPU availability is optional and workload-specific.
- Core contracts must support external, CPU-capable, or accelerated inference where requirements permit.
- No GPU vendor, memory capacity, accelerator count, or hosting model is assumed.

## Offline Support

- Full offline operation is not committed.
- The architecture should not preclude future cached study artifacts, flashcards, plans, and queued attempts.
- Offline behavior must define freshness, conflict resolution, encryption, revocation, and cross-device reconciliation before implementation.
- Generated or retrieval-dependent capabilities may require connectivity.

## Browser Support

- Target current stable versions of major standards-based browsers at release.
- Define an explicit support matrix and minimum versions during frontend planning.
- Critical journeys must not rely on one browser vendor.
- Progressive enhancement is preferred; unsupported environments require a clear message.

## Accessibility

- Target WCAG 2.2 AA for user-facing experiences unless a later approved requirement is stricter.
- Critical journeys must support keyboard navigation, screen readers, zoom, reflow, visible focus, sufficient contrast, and reduced motion.
- Generated content must preserve semantic structure and provide text alternatives where appropriate.
- Timed assessments and adaptive experiences must account for accommodations without inferring disability.
- Accessibility testing must include automated checks and human assistive-technology review.

## Security Constraints

- Apply least privilege, secure defaults, input validation, output encoding, and defense in depth.
- Treat uploads, retrieved content, prompts, plugins, model output, and external tools as untrusted.
- Domain plugins cannot broaden privileges implicitly.
- Secrets must not enter source, logs, prompts, datasets, evaluation artifacts, or client bundles.
- Privileged and model-mediated actions require authorization, audit context, and bounded effects.
- Threat modeling is mandatory before exposing uploads, agents, plugins, or public deployment.

## Privacy Constraints

- Collect only data necessary for a stated learning or operational purpose.
- Separate user-provided facts, observed events, and inferred attributes.
- Define consent, retention, export, correction, deletion, and de-identification behavior before personal data is stored.
- Do not use private learner data for training or evaluation without explicit lawful authorization and governance.
- Avoid logging raw learner content or prompts by default.
- Domain expansion must account for jurisdiction, age, and education-specific obligations.

## Future Constraints

- Deployment regions and data residency.
- Age restrictions and guardian consent.
- Content licensing and examination-authority terms.
- Cost ceilings per learner and per generated interaction.
- Model hosting, export control, and provider availability.
- Multi-tenancy and institution-specific isolation.
- Localization, multilingual quality, and right-to-left presentation.
- Disaster recovery, backup retention, and recovery objectives.

## Known Unknowns

- Initial release domain scope and representative workload.
- User geography, age profile, concurrency, and network conditions.
- Content formats, rights, corpus size, and update cadence.
- Required knowledge-state accuracy and acceptable uncertainty.
- Final latency, availability, retention, and recovery objectives.
- Upload threat model and moderation requirements.
- Regulatory classification and institutional procurement constraints.
- Model, embedding, vector-store, graph, and deployment choices.

