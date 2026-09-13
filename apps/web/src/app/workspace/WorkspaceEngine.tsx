"use client";

import { useEffect, useRef } from "react";
import { environmentRegistry } from "./environments";
import { WorkspaceProvider } from "./WorkspaceProvider";
import type { EnvironmentId, WorkspaceMemory } from "./WorkspaceTypes";
import { useWorkspace } from "./WorkspaceContext";
import { DocumentsEnvironment } from "./environments/documents/DocumentsEnvironment";
import { KnowledgeEnvironment } from "./environments/knowledge/KnowledgeEnvironment";
import { SearchEnvironment } from "./environments/search/SearchEnvironment";
import { StudyEnvironment } from "./environments/study/StudyEnvironment";
import { NotebookEnvironment } from "./environments/notebook/NotebookEnvironment";
import { FlashcardsEnvironment } from "./environments/flashcards/FlashcardsEnvironment";
import { QuizEnvironment } from "./environments/quiz/QuizEnvironment";
import { AnalyticsEnvironment } from "./environments/analytics/AnalyticsEnvironment";
import { StudioEnvironment } from "./environments/studio/StudioEnvironment";
import { WorkspaceContent, WorkspaceEmptyState, WorkspaceFooter, WorkspaceHeader, WorkspaceSurface, WorkspaceTransitionBoundary } from "@/components/workspace";

export function WorkspaceEngine({ 
  initialEnvironmentId, 
  initialHistory,
  initialMemory,
  sessionUserId,
  onLeave 
}: { 
  initialEnvironmentId: EnvironmentId; 
  initialHistory?: readonly EnvironmentId[];
  initialMemory?: Partial<Record<EnvironmentId, WorkspaceMemory>>;
  sessionUserId?: string | null;
  onLeave?: () => void;
}) { 
  return <WorkspaceProvider initialEnvironmentId={initialEnvironmentId} initialHistory={initialHistory} initialMemory={initialMemory} sessionUserId={sessionUserId}><WorkspaceEngineBody onLeave={onLeave} /></WorkspaceProvider>; 
}

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
  } else if (activeEnvironmentId === "knowledge") {
    environmentContent = <KnowledgeEnvironment />;
  } else if (activeEnvironmentId === "search") {
    environmentContent = <SearchEnvironment />;
  } else if (activeEnvironmentId === "study") {
    environmentContent = <StudyEnvironment />;
  } else if (activeEnvironmentId === "notebook") {
    environmentContent = <NotebookEnvironment />;
  } else if (activeEnvironmentId === "flashcards") {
    environmentContent = <FlashcardsEnvironment />;
  } else if (activeEnvironmentId === "quiz") {
    environmentContent = <QuizEnvironment />;
  } else if (activeEnvironmentId === "analytics") {
    environmentContent = <AnalyticsEnvironment />;
  } else if (activeEnvironmentId === "studio") {
    environmentContent = <StudioEnvironment />;
  } else {
    environmentContent = <WorkspaceEmptyState environment={environment} />;
  }

  return <WorkspaceTransitionBoundary><WorkspaceSurface><WorkspaceHeader environment={environment} onLeave={onLeave} /><WorkspaceContent>{environmentContent}</WorkspaceContent><WorkspaceFooter /></WorkspaceSurface></WorkspaceTransitionBoundary>;
}
