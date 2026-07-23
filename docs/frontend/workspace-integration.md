# Workspace Integration Foundation

This document outlines the architecture for connecting frontend workspaces to backend services while maintaining isolation from backend DTO changes and mock configurations.

## Core Philosophy

1. **Workspaces are agnostic to data source**: UI components do not know whether they are using live backend data or mock data.
2. **Errors are editorial**: We translate technical HTTP errors (404, 500, timeouts) into calm, user-friendly language suitable for the workspace.
3. **No UI state libraries**: We use the native `ResourceState<T>` pattern integrated within the existing context reducers, avoiding React Query or similar.

## Architecture Layers

### 1. API Client (`lib/api`)
The HTTP client handles generic transport concerns such as retry policies, timeouts, and JSON serialization. It uses `fetch` and supports an interceptor/middleware pattern for future cross-cutting concerns (authentication, logging). It explicitly supports cancellation via `AbortController`.

### 2. Services Layer (`lib/services`)
Services translate backend DTOs into frontend domain models. 
We have interfaces (e.g. `IDocumentService`) and explicit implementations for both Mock and Live environments (`MockDocumentService`, `LiveDocumentService`).

### 3. Provider Configuration (`lib/providers`)
A `ServiceProviderFactory` determines the active set of services based on configuration (`NEXT_PUBLIC_PROVIDER_MODE`). Workspaces retrieve services from `serviceProvider.getProvider()`, ensuring the React tree does not need a massive context wrapper just for dependency injection.

### 4. Hydration State (`lib/core/ResourceState.ts`)
To prevent spinner-heavy UI, we standardize data fetching around:
```ts
export type HydrationStatus = "idle" | "loading" | "ready" | "error" | "empty";

export interface ResourceState<T, E = Error> {
  status: HydrationStatus;
  data: T | null;
  error: E | null;
}
```
Workspaces use typographic loading states (e.g., "Retrieving knowledge...") to maintain a calm, continuous experience during data hydration.
