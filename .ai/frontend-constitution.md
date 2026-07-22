# Kogniq Frontend Design Constitution

This is **NOT** an implementation task.

Before proceeding with any future frontend work, I want you to pause and deeply analyze the current frontend architecture, interaction philosophy, and design language that has been established.

The goal is that **every future frontend implementation automatically follows these principles** without me having to repeat them.

This document becomes the permanent design constitution of Kogniq.

---

# First Task

Before implementing anything else:

- Analyze every current screen.
- Analyze every animation.
- Analyze every transition.
- Analyze every interaction.
- Analyze every typography decision.
- Analyze the workspace architecture.
- Analyze the overall emotional journey.

Treat everything currently implemented as the canonical baseline.

Future work must extend it instead of replacing it.

---

# What Kogniq Is

Kogniq is **NOT**

- an AI wrapper
- a ChatGPT clone
- a dashboard
- an admin panel
- a SaaS template
- a marketing website

Kogniq is a

**Knowledge Operating System**

The experience should feel closer to

- thinking
- studying
- understanding
- exploring
- reasoning

than chatting.

---

# The Product Philosophy

The user journey is fixed.

Arrival

↓

Access

↓

Intention

↓

Workspace

This sequence is now locked.

Never redesign it.

Every future feature must naturally plug into this journey.

---

# Workspace Philosophy

There is only ONE workspace.

Not multiple pages.

Not multiple dashboards.

Not multiple applications.

Everything happens inside one evolving workspace.

Documents

↓

Knowledge Graph

↓

Study

↓

Search

↓

Flashcards

↓

Quiz

↓

Chat

↓

Analytics

are simply different environments within the same workspace.

---

# Navigation Philosophy

Traditional navigation is forbidden unless explicitly approved.

Avoid introducing

- vertical sidebars
- horizontal navbars
- floating docks
- icon rails
- dashboard grids

Navigation should emerge naturally from context.

Changing environments should feel like changing perspective rather than changing applications.

---

# The Locus

The Locus is now Kogniq's primary interaction language.

Treat it like Cursor treats the editor.

Treat it like Figma treats the canvas.

Treat it like VS Code treats the editor.

It is part of the product identity.

Never replace it.

Never redesign it.

Never introduce another competing interaction.

The Locus should always remain calm, contextual, and purposeful.

---

# Typography Philosophy

Typography is the brand.

Not gradients.

Not illustrations.

Not icons.

Not logos.

The word

Kogniq

is already becoming the brand.

Protect that.

Typography creates hierarchy.

Typography creates emotion.

Typography creates navigation.

Typography creates rhythm.

Whenever unsure,

solve the problem using typography first.

---

# Motion Philosophy

Motion exists to explain state.

Never animate for decoration.

Every animation must answer

"What changed?"

Good motion:

- typography reorganizing
- workspace unfolding
- intention becoming workspace
- focus changing

Bad motion:

- floating panels
- bouncing buttons
- random fades
- decorative particles
- loading spectacles

Motion should feel invisible.

---

# Empty Space

Whitespace is a feature.

Never fill empty space because it looks empty.

Every element must justify its existence.

If removing something improves clarity,

remove it.

---

# Component Philosophy

Never think

"What component should I use?"

Instead think

"What is the simplest interface that communicates this?"

Avoid component-library thinking.

Do not recreate

- shadcn
- Radix defaults
- generic SaaS cards
- generic dashboard layouts

Design every interaction specifically for Kogniq.

---

# Dashboard Rule

Never call anything

Dashboard.

Never design a dashboard.

Never create an admin panel.

Never create a homepage after authentication.

The user enters a workspace.

Always.

---

# Feature Philosophy

Future features should not feel bolted on.

Documents

Knowledge Graph

Study

Search

Quiz

Flashcards

Analytics

Chat

should all feel natural extensions of the same environment.

---

# AI Philosophy

Kogniq is not centered around conversation.

Conversation is merely one capability.

Knowledge is the core.

Understanding is the goal.

Learning is the product.

---

# Design Inspirations

Use inspiration only.

Never imitate.

Good references:

Apple

Arc Browser

Linear

Obsidian

Raycast

Nothing

VS Code

Figma

GitHub

Academic publishing

Editorial magazines

Do NOT imitate their UI.

Instead imitate

their restraint.

their confidence.

their clarity.

---

# Accessibility

Accessibility is part of the design.

Not an afterthought.

Everything must support

- keyboard navigation
- focus management
- screen readers
- reduced motion
- semantic HTML
- responsive layouts

---

# Performance

Prefer

simple

fast

predictable

over

flashy

complex

over-engineered

---

# Every Future Decision

Before implementing any frontend feature, silently ask:

1. Does this feel like a Knowledge Operating System?

2. Am I accidentally creating another AI dashboard?

3. Can typography solve this instead of another component?

4. Can whitespace solve this instead of another element?

5. Does this make the workspace calmer?

6. Does this preserve the existing interaction language?

7. Does this feel like Kogniq?

If the answer to any of these is "no",

stop and redesign before implementing.

---

# Working Agreement

From this point onward, whenever I ask for a new frontend feature:

- First analyze how it fits the existing philosophy.
- Then explain any architectural concerns before implementation.
- Then implement it without breaking the design language.
- Never introduce generic AI patterns simply because they are common.
- Prioritize coherence over novelty.

This design constitution now overrides default UI conventions.
