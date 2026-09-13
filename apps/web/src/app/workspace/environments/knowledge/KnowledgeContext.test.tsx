import { describe, it, expect } from "vitest";
import { knowledgeReducer, initialState } from "./KnowledgeContext";
import type { KnowledgeState } from "./KnowledgeState";
import { MOCK_TRANSFORMER_GRAPH } from "./KnowledgeState";

describe("knowledgeReducer", () => {
  it("should return the initial state", () => {
    // @ts-expect-error - testing default branch
    const state = knowledgeReducer(initialState, { type: "UNKNOWN" });
    expect(state).toEqual(initialState);
  });

  it("should handle SET_GRAPH", () => {
    const action = {
      type: "SET_GRAPH" as const,
      payload: {
        status: "ready" as const,
        data: MOCK_TRANSFORMER_GRAPH,
        error: null,
        requestId: "req-1",
      },
    };

    const state = knowledgeReducer(initialState, action);

    expect(state.graph.status).toBe("ready");
    expect(state.graph.data).toEqual(MOCK_TRANSFORMER_GRAPH);
    expect(state.activeConceptId).toBeNull();
    expect(state.trail).toEqual([]);
  });

  it("should handle START_HYDRATION", () => {
    const action = {
      type: "START_HYDRATION" as const,
      payload: { requestId: "req-1" },
    };

    const state = knowledgeReducer(initialState, action);
    expect(state.graph.status).toBe("loading");
    expect(state.graph.requestId).toBe("req-1");
  });

  it("should handle ABORT_HYDRATION", () => {
    const loadingState: KnowledgeState = {
      ...initialState,
      graph: { ...initialState.graph, status: "loading", requestId: "req-1" },
    };

    const action = {
      type: "ABORT_HYDRATION" as const,
      payload: { requestId: "req-1" },
    };

    const state = knowledgeReducer(loadingState, action);
    expect(state.graph.status).toBe("idle");
  });

  it("should ignore ABORT_HYDRATION for stale request", () => {
    const loadingState: KnowledgeState = {
      ...initialState,
      graph: { ...initialState.graph, status: "loading", requestId: "req-2" },
    };

    const action = {
      type: "ABORT_HYDRATION" as const,
      payload: { requestId: "req-1" }, // Different ID
    };

    const state = knowledgeReducer(loadingState, action);
    expect(state.graph.status).toBe("loading"); // Remains loading
  });

  describe("SELECT_CONCEPT", () => {
    it("should select a new concept and add to trail", () => {
      const state = knowledgeReducer(initialState, {
        type: "SELECT_CONCEPT",
        payload: "concept-1",
      });

      expect(state.activeConceptId).toBe("concept-1");
      expect(state.trail).toEqual(["concept-1"]);
    });

    it("should append a different concept to the trail", () => {
      const state1 = knowledgeReducer(initialState, {
        type: "SELECT_CONCEPT",
        payload: "concept-1",
      });

      const state2 = knowledgeReducer(state1, {
        type: "SELECT_CONCEPT",
        payload: "concept-2",
      });

      expect(state2.activeConceptId).toBe("concept-2");
      expect(state2.trail).toEqual(["concept-1", "concept-2"]);
    });

    it("should truncate trail if selecting a concept already in trail", () => {
      let state = initialState;
      state = knowledgeReducer(state, { type: "SELECT_CONCEPT", payload: "concept-1" });
      state = knowledgeReducer(state, { type: "SELECT_CONCEPT", payload: "concept-2" });
      state = knowledgeReducer(state, { type: "SELECT_CONCEPT", payload: "concept-3" });

      expect(state.trail).toEqual(["concept-1", "concept-2", "concept-3"]);

      state = knowledgeReducer(state, { type: "SELECT_CONCEPT", payload: "concept-1" });

      expect(state.activeConceptId).toBe("concept-1");
      expect(state.trail).toEqual(["concept-1"]);
    });

    it("should clear selection and trail when payload is null", () => {
      let state = initialState;
      state = knowledgeReducer(state, { type: "SELECT_CONCEPT", payload: "concept-1" });
      state = knowledgeReducer(state, { type: "SELECT_CONCEPT", payload: null });

      expect(state.activeConceptId).toBeNull();
      expect(state.trail).toEqual([]);
    });
  });
});
