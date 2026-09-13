import { describe, it, expect } from "vitest";
import { analyticsReducer, initialAnalyticsState } from "./AnalyticsState";

describe("AnalyticsReducer", () => {
  it("should set time range", () => {
    const nextState = analyticsReducer(initialAnalyticsState, { type: "SET_TIME_RANGE", payload: "30d" });
    expect(nextState.timeRange).toBe("30d");
  });

  it("should transition to loading state", () => {
    const nextState = analyticsReducer(initialAnalyticsState, { type: "START_LOAD" });
    expect(nextState.status).toBe("loading");
    expect(nextState.error).toBeNull();
  });

  it("should transition to ready on success", () => {
    const metrics = { quizzes_completed: 1, average_quiz_accuracy: 0.5, flashcards_reviewed: 10 };
    const state = analyticsReducer(initialAnalyticsState, { type: "START_LOAD" });
    const nextState = analyticsReducer(state, { type: "LOAD_SUCCESS", payload: metrics });
    
    expect(nextState.status).toBe("ready");
    expect(nextState.metrics).toEqual(metrics);
    expect(nextState.error).toBeNull();
  });

  it("should transition to error state", () => {
    const error = new Error("Failed");
    const state = analyticsReducer(initialAnalyticsState, { type: "START_LOAD" });
    const nextState = analyticsReducer(state, { type: "LOAD_ERROR", payload: error });
    
    expect(nextState.status).toBe("error");
    expect(nextState.error).toBe(error);
    expect(nextState.metrics).toBeNull();
  });
});
