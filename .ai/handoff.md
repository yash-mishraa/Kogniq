# AI Agent Handoff Protocol

This protocol protects continuity across human and AI sessions.

## Mandatory Startup Checklist

Every future AI session **must**, before development or repository modification:

1. Read `.ai/design.md`.
2. Read `.ai/roadmap.md`.
3. Read `.ai/progress.md`.
4. Read `.ai/decisions.md`.
5. Read `.ai/techstack.md`.
6. Read `.ai/coding_rules.md`.
7. Read `.ai/glossary.md`.
8. Read `.ai/product_requirements.md`.
9. Read `.ai/system_constraints.md`.
10. Read `.ai/data_dictionary.md`.
11. Read `.ai/architecture_decision_flow.md`.
12. Read `.ai/system_blueprint.md`.

Only after completing this checklist may development begin. Then read the relevant directory README files, the current task, and any current prompt archive entry. Inspect the working tree and preserve unrelated changes. If instructions conflict, stop and surface the conflict rather than silently rewriting architecture.

Before implementing code, every AI agent must also consult the relevant contracts in `.ai/package_contracts.md`, `.ai/service_catalog.md`, `.ai/pipeline_catalog.md`, and `.ai/api_catalog.md`. Catalog entries describe plans, not evidence that a capability exists.

Kogniq is the product and platform. GATE is only the first planned learning-domain plugin and reference implementation. Future agents must keep reusable platform logic examination-neutral and must not infer that illustrative future domains are implemented.

## During the Session

- Work only within the requested stage and scope.
- Keep planned and implemented capabilities clearly distinct.
- Record durable architecture decisions as ADRs.
- Update documentation alongside architectural or ownership changes.
- Validate work in proportion to risk.

## Required End Sequence

- Update `.ai/progress.md`; append a Recent Sessions entry without deleting history.
- Update architecture, roadmap, technology status, or ADRs when affected.
- Report completed work, validation, unresolved issues, and the next safe action.
- Do not advance to another stage without explicit direction.

## Session Summary Template

```markdown
### YYYY-MM-DD — Stage N Prompt N

- **Completed:** <OUTCOMES>
- **Files Changed:** <FILES_OR_AREAS>
- **Architecture Changes:** <NONE_OR_SUMMARY>
- **New Decisions:** <NONE_OR_ADR_REFERENCES>
- **Known Issues:** <NONE_OR_ISSUES>
- **Validation:** <CHECKS_RUN>
- **Future Work:** <NEXT_EXPLICITLY_SCOPED_WORK>
```
