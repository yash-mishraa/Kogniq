"use client";

import { useEffect } from "react";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";
import { useStudio } from "@/app/workspace/environments/studio/StudioContext";
import { serviceProvider } from "@/lib/providers";
import type { StudioGraphConcept } from "@/app/workspace/environments/studio/StudioTypes";
import type { KnowledgeConcept } from "@/app/workspace/environments/knowledge/KnowledgeTypes";

export function StudioSidebar() {
  const { state, dispatch } = useStudio();
  const { memory } = useWorkspace();
  const documentId = memory.documents?.openedDocument;
  const { graph } = state;

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    
    async function hydrate() {
      const currentRequestId = crypto.randomUUID();
      dispatch({ type: "START_HYDRATION", payload: { requestId: currentRequestId } });
      
      if (!documentId) {
        if (isMounted) {
          dispatch({ type: "SET_GRAPH", payload: { status: "ready", data: { concepts: [] }, error: null, requestId: currentRequestId } });
        }
        return;
      }
      
      try {
        const data = await serviceProvider.getProvider().knowledge.getKnowledgeMap(documentId, controller.signal);
        if (isMounted) {
          // We map the KnowledgeConcept fields to StudioGraphConcept
          const concepts = data.concepts.map((c: KnowledgeConcept) => ({
            id: c.id,
            name: c.label,
            description: c.explanation
          }));
          dispatch({ type: "SET_GRAPH", payload: { status: "ready", data: { concepts }, error: null, requestId: currentRequestId } });
        }
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error && err.name === "AbortError") return;
          dispatch({ type: "SET_GRAPH", payload: { status: "error", data: null, error: err as Error, requestId: currentRequestId } });
        }
      }
    }
    
    hydrate();
    return () => {
      isMounted = false;
      controller.abort();
    };
    
  }, [dispatch, documentId]);

  if (graph.status === "loading") {
    return (
      <div className="w-80 flex-shrink-0 border-l border-ink/10 h-full flex items-center justify-center bg-paper-subtle">
        <p className="text-secondary text-sm">Loading concepts...</p>
      </div>
    );
  }

  if (graph.status === "error") {
    return (
      <div className="w-80 flex-shrink-0 border-l border-ink/10 h-full flex items-center justify-center bg-paper-subtle p-4 text-center">
        <p className="text-secondary text-sm">Unable to load knowledge concepts.</p>
      </div>
    );
  }

  const concepts = graph.data?.concepts || [];

  return (
    <div className="w-80 flex-shrink-0 border-l border-ink/10 h-full flex flex-col bg-paper-subtle">
      <div className="p-6 border-b border-ink/5">
        <h3 className="text-sm font-mono uppercase tracking-widest text-ink/60">Linked Knowledge</h3>
      </div>
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {concepts.length === 0 ? (
          <p className="text-secondary text-sm italic">No concepts found for this document.</p>
        ) : (
          concepts.map((concept: StudioGraphConcept) => (
            <div key={concept.id} className="flex flex-col gap-2">
              <h4 className="text-base font-medium text-ink">{concept.name}</h4>
              <p className="text-sm text-ink/70 leading-relaxed font-serif">{concept.description}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
