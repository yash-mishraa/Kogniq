# Planned Pipeline Catalog

Pipelines are future observable workflows, not implementations or technology selections. Each must preserve version lineage, authorization context, idempotency, retry policy, and failure quarantine. Logical services are cataloged in [`service_catalog.md`](service_catalog.md).

## Document Pipeline

- **Inputs:** Authorized source/upload, ownership, domain, license, access policy.
- **Outputs:** Governed Document version or a reviewable rejection.
- **Stages:** Validate request → scan/type-check → verify rights/provenance → extract metadata → persist source → register version → schedule eligible processing.
- **Dependencies:** Document, Authentication, Configuration, Logging; artifact/scanning adapters.
- **Failure Points:** Unsupported or malicious content, missing rights, duplicate/conflicting version, storage failure, policy rejection.
- **Future Improvements:** Rich format support, deduplication, incremental updates, reviewer workflow.

## OCR Pipeline

- **Inputs:** Approved image-based document/pages, language hints, OCR policy.
- **Outputs:** Positioned text, confidence, page/layout metadata, review flags.
- **Stages:** Render safely → preprocess → recognize → reconstruct layout → score confidence → validate → attach provenance.
- **Dependencies:** Document, Configuration, Logging; sandboxed rendering and OCR adapters.
- **Failure Points:** Corrupt/encrypted input, resource exhaustion, poor scan quality, language mismatch, table/formula loss.
- **Future Improvements:** Layout models, formula recognition, human correction, multilingual calibration.

## Cleaning Pipeline

- **Inputs:** Extracted text/layout, document provenance, cleaning policy version.
- **Outputs:** Normalized content plus a reversible transformation record.
- **Stages:** Detect structure → normalize encoding/whitespace → remove approved noise → preserve semantic blocks → validate → record diff/lineage.
- **Dependencies:** Document, Configuration, Logging.
- **Failure Points:** Semantic content removal, broken ordering, encoding loss, unsafe markup, non-idempotent transformation.
- **Future Improvements:** Domain-aware rules in plugins, table preservation, learned quality checks.

## Chunk Pipeline

- **Inputs:** Approved normalized document version, structural metadata, chunk policy.
- **Outputs:** Ordered Chunks with locations, overlap/context metadata, derivation version.
- **Stages:** Select strategy → segment structure → enforce size bounds → attach context → validate coverage/order → publish or quarantine.
- **Dependencies:** Document, Chunk, Configuration, Logging.
- **Failure Points:** Lost content, duplicated spans, broken tables/formulas, oversized chunks, unstable identifiers.
- **Future Improvements:** Hierarchical and semantic chunking, query-aware evaluation, multimodal regions.

## Embedding Pipeline

- **Inputs:** Eligible source objects, embedding model/configuration version, access scope.
- **Outputs:** Embeddings, lineage, usage, index-ready status.
- **Stages:** Select changed objects → authorize/minimize → batch → infer → validate dimensions/numerics → persist → emit index update.
- **Dependencies:** Embedding, source owner, Configuration, Logging, model adapter.
- **Failure Points:** Provider/model outage, rate limit, dimension mismatch, stale source, partial batch, cost budget breach.
- **Future Improvements:** Incremental refresh, model migration, quantization, multimodal representations.

## Retrieval Pipeline

- **Inputs:** Query, domain/curriculum scope, identity filters, retrieval policy.
- **Outputs:** Ranked permitted evidence with provenance and stage metadata.
- **Stages:** Validate/rewrite query → select indexes → retrieve candidates → enforce filters → fuse → rerank → diversify → validate evidence.
- **Dependencies:** Retrieval, Embedding, Chunk, Document, Knowledge Graph, Configuration, Logging.
- **Failure Points:** Empty/poisoned result, authorization leakage, stale index, reranker failure, latency or cost budget breach.
- **Future Improvements:** Adaptive hybrid search, graph expansion, learned routing, calibrated relevance.

## Generation Pipeline

- **Inputs:** Authorized task, retrieved evidence, instructions, learner context, generation policy.
- **Outputs:** Structured response, uncertainty, citations, usage and version metadata, or safe refusal.
- **Stages:** Minimize context → defend against injection → assemble prompt → infer/stream → validate structure/safety → verify grounding → attach citations → persist eligible provenance.
- **Dependencies:** Generation, Retrieval, Citation, Configuration, Logging, model adapter.
- **Failure Points:** Injection, unsupported claim, unsafe output, malformed response, provider failure, cancellation, timeout.
- **Future Improvements:** Claim-level verification, model routing, adaptive explanation style, stronger constrained decoding.

## Evaluation Pipeline

- **Inputs:** Versioned subject, evaluation dataset, metrics, slices, configuration, thresholds.
- **Outputs:** Evaluation Result, comparison, artifacts, gate outcome.
- **Stages:** Validate lineage → isolate run → execute examples → collect outputs → compute metrics/slices → human review where required → compare thresholds → publish report.
- **Dependencies:** Evaluation, Experiment, Configuration, Logging, public subject interfaces.
- **Failure Points:** Dataset leakage, nondeterminism, incomplete run, invalid metric, reviewer disagreement, incomparable versions.
- **Future Improvements:** Statistical power analysis, continuous evaluation, richer adjudication, cost/latency quality frontier.

## Question Generation Pipeline

- **Inputs:** Approved concepts, curriculum scope, governed sources, generation policy, item specification.
- **Outputs:** Draft Question proposals with answers, rationales, citations, and validation findings.
- **Stages:** Select objective → retrieve sources → generate draft → solve/check independently → map concepts → validate format/citations → deduplicate → route to subject review.
- **Dependencies:** Question, Retrieval, Generation, Citation, Knowledge Graph, Evaluation.
- **Failure Points:** Wrong answer, ambiguity, leakage, invalid difficulty, unsupported rationale, duplicate/copyright concern.
- **Future Improvements:** Adversarial review, calibrated difficulty, variant generation, psychometric feedback.

## Recommendation Pipeline

- **Inputs:** Learner goal, authorized knowledge state, curriculum graph, candidate actions, constraints.
- **Outputs:** Ranked Recommendations with rationale, uncertainty, and policy metadata.
- **Stages:** Validate context → generate candidates → enforce eligibility → score → diversify → apply time/prerequisite constraints → explain → policy-check → present.
- **Dependencies:** Recommendation, ML inference, Knowledge Graph, Question, Analytics, Configuration.
- **Failure Points:** Stale state, unfair or repetitive ranking, impossible workload, privacy overreach, missing rationale.
- **Future Improvements:** Outcome-aware ranking, counterfactual explanations, learner preference adaptation, educator constraints.

## Revision Pipeline

- **Inputs:** Accepted recommendations, learner availability, target date, retention evidence, user edits.
- **Outputs:** Editable Revision Plan and Revision Tasks.
- **Stages:** Select eligible work → estimate effort → order prerequisites → space review → fit availability → explain → validate feasibility → publish editable plan → monitor outcomes.
- **Dependencies:** Revision, Recommendation, Knowledge Graph, Question, Configuration.
- **Failure Points:** Overloaded schedule, conflicting prerequisites, stale goal, timezone error, ignored user preference.
- **Future Improvements:** Adaptive rescheduling, offline reconciliation, calendar integration, retention optimization.

## Knowledge Graph Pipeline

- **Inputs:** Versioned curriculum, concept/edge proposals, mappings, provenance, domain namespace.
- **Outputs:** Validated graph version, report, rejected/quarantined proposals, migration metadata.
- **Stages:** Parse → normalize identifiers → validate schema → resolve namespace → check invariants/cycles → verify provenance → reviewer approval → publish version → rebuild derived views.
- **Dependencies:** Knowledge Graph, Document, Configuration, Logging, domain plugin contract.
- **Failure Points:** Identifier collision, invalid edge semantics, unsupported cycles, cross-domain leakage, missing evidence, incompatible version.
- **Future Improvements:** Assisted curation, confidence aggregation, temporal graphs, cross-domain mapping review.

## Training Pipeline

- **Inputs:** Approved task, governed dataset/splits, feature/model configuration, baseline and resource budget.
- **Outputs:** Candidate model artifact, model card inputs, metrics, lineage, failure report.
- **Stages:** Validate data/consent → freeze versions → build features → train → validate → compare baseline → assess calibration/fairness/safety → register candidate or reject.
- **Dependencies:** ML, Experiment, Evaluation, Configuration, Logging, artifact registry adapters.
- **Failure Points:** Leakage, non-reproducibility, unstable training, budget breach, weak baseline result, governance failure.
- **Future Improvements:** Distributed training if justified, automated tuning with budgets, stronger lineage and bias analysis.

## Inference Pipeline

- **Inputs:** Authorized typed request, model version/policy, feature context, latency/cost budget.
- **Outputs:** Typed prediction/representation, uncertainty, model metadata, runtime checks.
- **Stages:** Validate/authorize → construct features → select approved model → infer → validate output → calibrate/postprocess → policy-check → return and observe.
- **Dependencies:** ML, Configuration, Logging, model registry/serving adapter.
- **Failure Points:** Feature skew, unavailable model, malformed output, drift, timeout, resource saturation.
- **Future Improvements:** Safe model routing, batching, shadow evaluation, hardware-aware optimization.

