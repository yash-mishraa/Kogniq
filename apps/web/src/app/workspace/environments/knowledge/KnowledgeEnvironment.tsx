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

import { serviceProvider } from "@/lib/providers";

function KnowledgeEnvironmentBody() {
  const { state, dispatch } = useKnowledge();
  const { remember } = useWorkspace();
  const { graph } = state;
  
  useEffect(() => {
    remember("knowledge", {
      focusTarget: "locus"
    });
  }, [remember]);

  useEffect(() => {
    if (graph.status !== "idle") return;
    
    const controller = new AbortController();
    
    async function hydrate() {
      dispatch({ type: "SET_GRAPH", payload: { ...graph, status: "loading" } });
      try {
        const data = await serviceProvider.getProvider().knowledge.getKnowledgeMap(controller.signal);
        dispatch({ type: "SET_GRAPH", payload: { status: "ready", data, error: null } });
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") return;
        dispatch({ type: "SET_GRAPH", payload: { status: "error", data: null, error: err as Error } });
      }
    }
    
    hydrate();
    return () => controller.abort();
  }, [graph.status, dispatch, graph]);

  if (graph.status === "loading") {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-secondary text-lg">Retrieving knowledge...</p>
      </div>
    );
  }

  if (graph.status === "error") {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-secondary text-lg">Unable to retrieve this knowledge right now. Try again shortly.</p>
      </div>
    );
  }

  if (!graph.data || graph.data.concepts.length === 0) {
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
