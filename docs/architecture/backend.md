# Backend Services

**Status:** Planned (Not Yet Implemented)

## Purpose
To provide the REST and GraphQL APIs necessary for client applications to interact with the Kogniq core domain.

## Expected Responsibilities
- Handling HTTP requests and routing.
- Authenticating users and managing sessions.
- Exposing the `content`, `learning`, and `education` domains via a unified API gateway (e.g. FastAPI).
- Connecting to persistent storage layers (PostgreSQL, Vector Databases).

## Relationship to Existing Packages
The Backend serves as the Composition Root. It will import the pure domain logic from `packages/` and wire it up to real infrastructure (databases, message queues).

---
*Return to [Architecture Index](README.md).*
