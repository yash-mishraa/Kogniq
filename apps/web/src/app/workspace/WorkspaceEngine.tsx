"use client";

import { useEffect, useRef } from "react";
import { environmentRegistry } from "./environments";
import { WorkspaceProvider } from "./WorkspaceProvider";
import type { EnvironmentId } from "./WorkspaceTypes";
import { useWorkspace } from "./WorkspaceContext";
import { DocumentsEnvironment } from "./environments/documents/DocumentsEnvironment";
import { WorkspaceContent, WorkspaceEmptyState, WorkspaceFooter, WorkspaceHeader, WorkspaceSurface, WorkspaceTransitionBoundary } from "@/components/workspace";

export function WorkspaceEngine({ initialEnvironmentId, onLeave }: { initialEnvironmentId: EnvironmentId; onLeave?: () => void }) { return <WorkspaceProvider initialEnvironmentId={initialEnvironmentId}><WorkspaceEngineBody onLeave={onLeave} /></WorkspaceProvider>; }

function WorkspaceEngineBody({ onLeave }: { onLeave?: () => void }) {
  const { activeEnvironmentId, memory } = useWorkspace();
  const environment = environmentRegistry.getEnvironment(activeEnvironmentId);
  const memoryRef = useRef(memory);
  useEffect(() => { memoryRef.current = memory; }, [memory]);
  useEffect(() => { const remembered = memoryRef.current[activeEnvironmentId]; const selector = remembered?.focusTarget ? `[data-workspace-focus="${remembered.focusTarget}"] input` : "[data-workspace-focus=\"locus\"] input"; const target = document.querySelector<HTMLInputElement>(selector); target?.focus(); }, [activeEnvironmentId]);
  if (!environment) return null;

  let environmentContent;
  if (activeEnvironmentId === "documents") {
    environmentContent = <DocumentsEnvironment />;
  } else {
    environmentContent = <WorkspaceEmptyState environment={environment} />;
  }

  return <WorkspaceTransitionBoundary><WorkspaceSurface><WorkspaceHeader environment={environment} onLeave={onLeave} /><WorkspaceContent>{environmentContent}</WorkspaceContent><WorkspaceFooter /></WorkspaceSurface></WorkspaceTransitionBoundary>;
}
