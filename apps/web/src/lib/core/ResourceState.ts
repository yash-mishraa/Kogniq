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
  requestId?: string;
}

export function createInitialResourceState<T>(): ResourceState<T> {
  return {
    status: "idle",
    data: null,
    error: null,
    requestId: undefined,
  };
}

/**
 * Safely aborts a resource hydration only if the aborted request matches
 * the currently active requestId. This prevents stale aborts from overwriting
 * newer hydration requests.
 */
export function abortResourceHydration<T, E>(state: ResourceState<T, E>, requestId: string): ResourceState<T, E> {
  if (state.requestId === requestId) {
    return { ...state, status: "idle" };
  }
  return state;
}

/**
 * Safely starts a resource hydration by setting the status to loading
 * and assigning the new requestId, preserving existing data.
 */
export function startResourceHydration<T, E>(state: ResourceState<T, E>, requestId: string): ResourceState<T, E> {
  return { ...state, status: "loading", requestId };
}
