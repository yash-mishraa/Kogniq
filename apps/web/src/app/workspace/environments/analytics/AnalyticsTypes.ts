import { AnalyticsMetrics } from "@/lib/services/live/LiveAnalyticsService";

export type TimeRange = "7d" | "30d" | "all";

export interface AnalyticsState {
  status: "idle" | "loading" | "ready" | "error";
  error: Error | null;
  timeRange: TimeRange;
  metrics: AnalyticsMetrics | null;
}

export type AnalyticsAction =
  | { type: "SET_TIME_RANGE"; payload: TimeRange }
  | { type: "START_LOAD" }
  | { type: "LOAD_SUCCESS"; payload: AnalyticsMetrics }
  | { type: "LOAD_ERROR"; payload: Error };
