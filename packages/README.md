# Packages

`packages/` contains reusable Kogniq capabilities and bounded domain contexts. Each package owns a public boundary and keeps implementation details private.

Applications may compose packages; packages must not import applications. Cross-package dependencies are limited by [`.ai/package_contracts.md`](../.ai/package_contracts.md), and exam-specific behavior must remain outside the platform core.

No package currently contains source code, dependency manifests, or runtime configuration.

