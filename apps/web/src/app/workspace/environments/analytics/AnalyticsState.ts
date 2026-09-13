import { AnalyticsAction, AnalyticsState } from "./AnalyticsTypes";

export const initialAnalyticsState: AnalyticsState = {
  status: "idle",
  error: null,
  timeRange: "7d",
  metrics: null,
};

export function analyticsReducer(state: AnalyticsState, action: AnalyticsAction): AnalyticsState {
  switch (action.type) {
    case "SET_TIME_RANGE":
      return { ...state, timeRange: action.payload };
    case "START_LOAD":
      return { ...state, status: "loading", error: null };
    case "LOAD_SUCCESS":
      return { ...state, status: "ready", metrics: action.payload, error: null };
    case "LOAD_ERROR":
      return { ...state, status: "error", error: action.payload, metrics: null };
    default:
      return state;
  }
}
