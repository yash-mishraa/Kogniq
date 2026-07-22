"use client";

import { createContext, useContext } from "react";
import type { EnvironmentId, WorkspaceMemory, WorkspaceState } from "./WorkspaceTypes";

export interface WorkspaceContextValue extends WorkspaceState {
  switchEnvironment: (environmentId: EnvironmentId) => void;
  remember: (environmentId: EnvironmentId, memory: WorkspaceMemory) => void;
}

export const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function useWorkspace() {
  const value = useContext(WorkspaceContext);
  if (!value) throw new Error("useWorkspace must be used inside WorkspaceProvider.");
  return value;
}
