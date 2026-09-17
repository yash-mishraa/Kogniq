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
  sessionUserId,
  children 
}: { 
  initialEnvironmentId: EnvironmentId; 
  initialHistory?: readonly EnvironmentId[];
  initialMemory?: Partial<Record<EnvironmentId, WorkspaceMemory>>;
  sessionUserId?: string | null;
  children: ReactNode; 
}) {
  const getStorageKey = useCallback(() => {
    return sessionUserId ? `kogniq_workspace_state_${sessionUserId}` : "kogniq_workspace_state";
  }, [sessionUserId]);

  const [activeEnvironmentId, setActiveEnvironmentId] = useState(initialEnvironmentId);
  const [history, setHistory] = useState<readonly EnvironmentId[]>(() => {
    if (typeof window !== "undefined") {
      try {
        const saved = localStorage.getItem(getStorageKey());
        if (saved) return JSON.parse(saved).history || initialHistory || [initialEnvironmentId];
      } catch {}
    }
    return initialHistory || [initialEnvironmentId];
  });
  const [memory, setMemory] = useState<Partial<Record<EnvironmentId, WorkspaceMemory>>>(() => {
    if (typeof window !== "undefined") {
      try {
        const saved = localStorage.getItem(getStorageKey());
        if (saved) return JSON.parse(saved).memory || initialMemory || {};
      } catch {}
    }
    return initialMemory || {};
  });
  
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const savedStr = localStorage.getItem(getStorageKey());
        if (savedStr) {
          const saved = JSON.parse(savedStr);
          if (saved.history) setHistory(saved.history);
          if (saved.memory) setMemory(saved.memory);
          setActiveEnvironmentId(initialEnvironmentId);
          return;
        }
      } catch {}
    }
    // If no saved state, reset to initials
    setHistory(initialHistory || [initialEnvironmentId]);
    setMemory(initialMemory || {});
    setActiveEnvironmentId(initialEnvironmentId);
  }, [getStorageKey, initialEnvironmentId, initialHistory, initialMemory]);
  
  useEffect(() => {
    const state: SerializedWorkspaceState = { activeEnvironmentId, history, memory };
    localStorage.setItem(getStorageKey(), JSON.stringify(state));
  }, [activeEnvironmentId, history, memory, getStorageKey]);

  const switchEnvironment = useCallback((environmentId: EnvironmentId) => { setActiveEnvironmentId(environmentId); setHistory((current) => current[current.length - 1] === environmentId ? current : [...current, environmentId]); }, []);
  const remember = useCallback((environmentId: EnvironmentId, patch: WorkspaceMemory) => { setMemory((current) => ({ ...current, [environmentId]: { ...current[environmentId], ...patch } })); }, []);
  const value = useMemo(() => ({ activeEnvironmentId, history, memory, switchEnvironment, remember }), [activeEnvironmentId, history, memory, switchEnvironment, remember]);
  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}
