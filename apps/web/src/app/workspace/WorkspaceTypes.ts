export type EnvironmentId = "documents" | "graph" | "knowledge" | "search" | "studio" | "study" | "notebook" | "flashcards" | "quiz" | "analytics";

export type WorkspaceMotionProfile = "reading" | "spatial" | "evidence" | "focused" | "measured";
export type WorkspaceRhythm = "editorial" | "canvas" | "vertical" | "sequential" | "structured";

export interface EnvironmentMetadata {
  id: EnvironmentId;
  title: string;
  description: string;
  locusPlaceholder: string;
  motionProfile: WorkspaceMotionProfile;
  rhythm: WorkspaceRhythm;
  contextualPanels?: readonly string[];
}

export interface WorkspaceMemory {
  focusTarget?: string;
  scrollPosition?: number;
  selectedContext?: string;
  openedDocument?: string;
  readingPosition?: number;
}

export interface WorkspaceState {
  activeEnvironmentId: EnvironmentId;
  history: readonly EnvironmentId[];
  memory: Partial<Record<EnvironmentId, WorkspaceMemory>>;
}
