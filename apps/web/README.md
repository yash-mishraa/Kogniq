# Web Application

## Purpose

Composition root for Kogniq's accessible browser experience. Its first product flow is a deliberately minimal progression from Arrival through Access and Intention into a contextual Workspace.

## Responsibilities

Own presentation, interaction state, accessibility, safe rendering, progressive feedback, and consumption of supported application contracts.

## Public Interface

The root route implements the product contract. Reusable behavioral primitives live in `src/components/ui`; the visible experience belongs to `src/components/experience` and is guided by the Locus interaction language.

## Dependencies

May use browser-safe exports from `packages/shared` and supported clients for `apps/api`. It must not import server or intelligence internals.

## Future Expansion

Potential experience areas include learning workspaces, curriculum exploration, assessment, progress, revision, and reviewer tools after product requirements are approved.

## Ownership

Frontend/product experience — Yash Mishra.

## What Does NOT Belong Here

Domain authority, secrets, database access, model or retrieval pipelines, agent tools, server-only configuration, or examination-specific core logic.
