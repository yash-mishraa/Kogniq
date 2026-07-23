"use client";

import { type ReactNode, useCallback, useMemo, useState, useEffect } from "react";
import { WorkspaceContext } from "./WorkspaceContext";
import type { EnvironmentId, WorkspaceMemory } from "./WorkspaceTypes";

export interface SerializedWorkspaceState {
  activeEnvironmentId: EnvironmentId;
  history: readonly EnvironmentId[];
  memory: Partial<Record<EnvironmentId, WorkspaceMemory>>;
}

export function WorkspaceProvider({ 
  initialEnvironmentId, 
  initialHistory,
  initialMemory,
  children 
}: { 
  initialEnvironmentId: EnvironmentId; 
  initialHistory?: readonly EnvironmentId[];
  initialMemory?: Partial<Record<EnvironmentId, WorkspaceMemory>>;
  children: ReactNode; 
}) {
  const [activeEnvironmentId, setActiveEnvironmentId] = useState(initialEnvironmentId);
  const [history, setHistory] = useState<readonly EnvironmentId[]>(initialHistory || [initialEnvironmentId]);
  const [memory, setMemory] = useState<Partial<Record<EnvironmentId, WorkspaceMemory>>>(initialMemory || {});
  
  useEffect(() => {
    const state: SerializedWorkspaceState = { activeEnvironmentId, history, memory };
    localStorage.setItem("kogniq_workspace_state", JSON.stringify(state));
  }, [activeEnvironmentId, history, memory]);

  const switchEnvironment = useCallback((environmentId: EnvironmentId) => { setActiveEnvironmentId(environmentId); setHistory((current) => current[current.length - 1] === environmentId ? current : [...current, environmentId]); }, []);
  const remember = useCallback((environmentId: EnvironmentId, patch: WorkspaceMemory) => { setMemory((current) => ({ ...current, [environmentId]: { ...current[environmentId], ...patch } })); }, []);
  const value = useMemo(() => ({ activeEnvironmentId, history, memory, switchEnvironment, remember }), [activeEnvironmentId, history, memory, switchEnvironment, remember]);
  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}
