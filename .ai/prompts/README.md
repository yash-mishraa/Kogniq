# Prompt Archive

## Purpose

This directory is the manual archive for approved repository prompts. It preserves the exact scope, constraints, completion conditions, and historical sequence of requested work. It is not a scratchpad, generated prompt library, or substitute for [`../progress.md`](../progress.md).

## Prompt Naming Convention

Use:

```text
stage-<stage>-prompt-<number>-<short-kebab-title>.md
```

Examples:

- `stage-0.5-prompt-1-repository-intelligence-layer.md`
- `stage-2-prompt-3-backend-contract-review.md`

Use lowercase ASCII, hyphens, the stated stage and prompt number, and a short descriptive title. Do not rename archived prompts after work begins; add a clearly linked correction if necessary.

## Folder Organization

Keep prompts at this directory level until volume justifies stage subdirectories. If organization changes, preserve names and history through a documented migration. This README is the only file created here automatically during Stage 0.5; future prompt text will be stored manually.

## How Prompts Are Archived

1. Copy the approved prompt verbatim into a new Markdown file.
2. Add archive metadata above it: received date, stage, prompt number, status, and related progress-session heading.
3. Preserve stop conditions and later corrections.
4. Mark a prompt completed only after validation and the progress entry exist.
5. Never overwrite or silently edit historical prompt text.

Do not archive secrets, personal data, credentials, or inaccessible external context.

## How Future AI Agents Should Use Prompts

AI agents should read the current authorized prompt after completing the mandatory startup checklist in [`../handoff.md`](../handoff.md). Archived prompts provide historical scope, not standing authorization to repeat or continue work. When an archive conflicts with an accepted ADR or newer explicit instruction, surface the conflict and follow the architecture decision process.

## Prompt Numbering

Prompt numbers are scoped to their stated repository stage and should increase monotonically within that stage. Decimal stages such as `0.5` are valid. Corrections retain the original number and receive a suffix such as `-amendment-1`; they do not rewrite history.

## Prompt History

[`../progress.md`](../progress.md) is the authoritative session history and links outcomes to prompt numbers. This archive preserves inputs. An archived prompt should reference its corresponding progress entry; the progress entry should list the prompt archive file when one exists.

## Prompt Review Process

- Confirm the prompt has a unique name and complete metadata.
- Check scope against the current repository stage and accepted ADRs.
- Identify architecture, product, data, security, privacy, or dependency implications.
- Resolve contradictions before implementation.
- Verify stop conditions and expected documentation updates.
- After completion, verify that progress and decision records accurately describe the result.

