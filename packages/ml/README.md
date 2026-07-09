# ML Package

## Purpose

Reserve the reusable boundary for learner modeling, knowledge tracing, ranking, training, and inference.

## Responsibilities

Future task definitions, feature contracts, model adapters, reproducible training, validation, registration metadata, calibration, and monitoring signals.

## Public Interface

Planned typed training and inference contracts plus model metadata. No model, feature, training pipeline, or inference implementation exists.

## Dependencies

May depend on `packages/shared` and approved public graph contracts. Runtime workflows access ML through public ports.

## Future Expansion

Knowledge-state estimation, recommendation ranking, difficulty estimation, drift analysis, and additional model families after baseline evaluation.

## Ownership

ML engineering and applied science — Yash Mishra.

## What Does NOT Belong Here

Product APIs, UI, raw ungoverned data, one-off experiments, domain-specific shortcuts, committed large model artifacts, secrets, or direct learner workflow ownership.
