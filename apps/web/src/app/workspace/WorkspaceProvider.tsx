"use client";

import { type ReactNode, useCallback, useMemo, useState } from "react";
import { WorkspaceContext } from "./WorkspaceContext";
import type { EnvironmentId, WorkspaceMemory } from "./WorkspaceTypes";

export function WorkspaceProvider({ initialEnvironmentId, children }: { initialEnvironmentId: EnvironmentId; children: ReactNode }) {
  const [activeEnvironmentId, setActiveEnvironmentId] = useState(initialEnvironmentId);
  const [history, setHistory] = useState<readonly EnvironmentId[]>([initialEnvironmentId]);
  const [memory, setMemory] = useState<Partial<Record<EnvironmentId, WorkspaceMemory>>>({});
  const switchEnvironment = useCallback((environmentId: EnvironmentId) => { setActiveEnvironmentId(environmentId); setHistory((current) => current[current.length - 1] === environmentId ? current : [...current, environmentId]); }, []);
  const remember = useCallback((environmentId: EnvironmentId, patch: WorkspaceMemory) => { setMemory((current) => ({ ...current, [environmentId]: { ...current[environmentId], ...patch } })); }, []);
  const value = useMemo(() => ({ activeEnvironmentId, history, memory, switchEnvironment, remember }), [activeEnvironmentId, history, memory, switchEnvironment, remember]);
  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}
