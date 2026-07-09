# Evaluation Package

## Purpose

Reserve an independent boundary for quality measurement and release evidence.

## Responsibilities

Future evaluation datasets, metrics, rubrics, harnesses, slices, regression comparison, human adjudication, reports, and release gates.

## Public Interface

Planned evaluation specifications, run requests, result schemas, comparison reports, and threshold decisions. No harness exists.

## Dependencies

May depend on `packages/shared` and public or black-box interfaces of evaluated subjects. Production packages must not depend on evaluation implementation.

## Future Expansion

Retrieval, model, agent, safety, accessibility, performance, and learning-effectiveness evaluation after each subject has measurable criteria.

## Ownership

Evaluation with product, subject, safety, and ML reviewers — Yash Mishra.

## What Does NOT Belong Here

Production serving logic, hidden release exceptions, training-data leakage, cherry-picked demonstrations, private learner data, or exploratory scratch work.
