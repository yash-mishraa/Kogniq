import { describe, it, expect } from "vitest";
import { studioReducer, initialState as initialStudioState } from "./StudioContext";
import type { StudioAction, StudioState } from "./StudioState";

describe("studioReducer", () => {
  it("should initialize with initial state", () => {
    expect(initialStudioState).toEqual({
      isPreview: false,
      graph: {
        status: "idle",
        data: null,
        error: null,
        requestId: undefined,
      },
    });
  });

  it("should handle SET_PREVIEW", () => {
    const action: StudioAction = { type: "SET_PREVIEW", payload: true };
    const nextState = studioReducer(initialStudioState, action);
    expect(nextState.isPreview).toBe(true);

    const action2: StudioAction = { type: "SET_PREVIEW", payload: false };
    const nextState2 = studioReducer(nextState, action2);
    expect(nextState2.isPreview).toBe(false);
  });

  it("should handle START_HYDRATION", () => {
    const action: StudioAction = {
      type: "START_HYDRATION",
      payload: { requestId: "req-1" },
    };
    const nextState = studioReducer(initialStudioState, action);
    expect(nextState.graph.status).toBe("loading");
    expect(nextState.graph.requestId).toBe("req-1");
  });

  it("should handle SET_GRAPH when requestId matches", () => {
    const state: StudioState = {
      ...initialStudioState,
      graph: { ...initialStudioState.graph, status: "loading", requestId: "req-1" },
    };

    const action: StudioAction = {
      type: "SET_GRAPH",
      payload: {
        status: "ready",
        data: {
          concepts: [{ id: "c1", name: "Concept", description: "Desc" }],
        },
        error: null,
        requestId: "req-1",
      },
    };

    const nextState = studioReducer(state, action);
    expect(nextState.graph.status).toBe("ready");
    expect(nextState.graph.data?.concepts).toHaveLength(1);
  });

  it("should ignore SET_GRAPH when requestId does not match", () => {
    const state: StudioState = {
      ...initialStudioState,
      graph: { ...initialStudioState.graph, status: "loading", requestId: "req-2" },
    };

    const action: StudioAction = {
      type: "SET_GRAPH",
      payload: {
        status: "ready",
        data: { concepts: [] },
        error: null,
        requestId: "req-1",
      },
    };

    const nextState = studioReducer(state, action);
    expect(nextState).toBe(state);
  });
});
