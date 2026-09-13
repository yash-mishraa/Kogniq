import type { EnvironmentMetadata } from "../../WorkspaceTypes";

export const analyticsEnvironment: EnvironmentMetadata = {
  id: "analytics",
  title: "Analytics",
  description: "Track your learning progress.",
  locusPlaceholder: "View your metrics",
  motionProfile: "measured",
  rhythm: "structured",
};

export { AnalyticsEnvironment } from "./AnalyticsEnvironment";
