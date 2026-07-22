"use client";

import { KnowledgeProvider, useKnowledge } from "./KnowledgeContext";
import { 
  KnowledgeSurface, 
  KnowledgeEmptyState, 
  KnowledgeMap, 
  KnowledgeInspector,
  KnowledgeTrail
} from "@/components/knowledge";
import { useEffect } from "react";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";

function KnowledgeEnvironmentBody() {
  const { state } = useKnowledge();
  const { remember } = useWorkspace();
  
  // Note: locusPlaceholder is now part of EnvironmentMetadata, but if we need dynamic
  // context we can use memory. For now, the environment provides the default.
  useEffect(() => {
    // We don't necessarily need to set locusPrompt in memory if it's in metadata,
    // but if we do, here's how we'd do it for focus restoration
    remember("knowledge", {
      focusTarget: "locus"
    });
  }, [remember]);

  if (!state.graph || state.graph.concepts.length === 0) {
    return <KnowledgeEmptyState />;
  }

  return (
    <KnowledgeSurface>
      <KnowledgeTrail />
      <KnowledgeMap />
      <KnowledgeInspector />
    </KnowledgeSurface>
  );
}

export function KnowledgeEnvironment() {
  return (
    <KnowledgeProvider>
      <KnowledgeEnvironmentBody />
    </KnowledgeProvider>
  );
}
