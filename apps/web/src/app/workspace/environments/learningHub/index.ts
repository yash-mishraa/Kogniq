import { lazy } from "react";
import type { EnvironmentMetadata } from "../../WorkspaceTypes";

export const metadata: EnvironmentMetadata = {
  id: "learningHub",
  title: "Learning Hub",
  description: "View and manage content intelligence resources.",
  locusPlaceholder: "Search resources...",
  motionProfile: "spatial",
  rhythm: "vertical",
};

const LearningHubEnvironmentComponent = lazy(() => import("./LearningHubEnvironment").then(mod => ({ default: mod.LearningHubEnvironment })));

export const learningHubEnvironment = {
  ...metadata,
  component: LearningHubEnvironmentComponent,
};
