/**
 * A standard hydration lifecycle model for resources.
 * This is used across environments (Search, Study, Documents, etc.) to 
 * represent the unified state of a resource fetching/preparation cycle.
 */
export type HydrationStatus = "idle" | "loading" | "ready" | "error" | "empty";

export interface ResourceState<T, E = Error> {
  status: HydrationStatus;
  data: T | null;
  error: E | null;
}

export function createInitialResourceState<T>(): ResourceState<T> {
  return {
    status: "idle",
    data: null,
    error: null,
  };
}
