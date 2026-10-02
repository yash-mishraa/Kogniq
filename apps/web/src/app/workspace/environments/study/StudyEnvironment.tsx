"use client";

import { useStudy, StudyProvider } from "./StudyContext";
import { StudySurface, StudyEmptyState, StudyPerspective, StudyTimeline, StudyNavigator, StudyContextPanel } from "@/components/study";

import { useEffect, useState } from "react";
import { serviceProvider } from "@/lib/providers";

import { useWorkspace } from "../../WorkspaceContext";
import { TutorChatPanel } from "./TutorChatPanel";
import { useDocuments } from "../documents/DocumentsContext";
import { ProcessingState } from "@/components/ui/processing-state";

function StudyEnvironmentBody() {
  const { state, dispatch } = useStudy();
  const { memory, remember } = useWorkspace();
  const { state: docsState } = useDocuments();
  const documentId = memory.documents?.openedDocument;
  
  const activeDoc = docsState.documents.data?.find(d => d.id === documentId);
  const isReady = activeDoc?.status === "Ready";

  // Automatically transition the Study state machine when the active document changes
  useEffect(() => {
    if (documentId) {
      if (!state.isStudying || (state.material.data && state.material.data.concept.id !== documentId)) {
        dispatch({ type: "START_STUDY", payload: { status: "idle", data: null, error: null } });
      }
    } else if (state.isStudying) {
      dispatch({ type: "END_STUDY" });
    }
  }, [documentId, state.isStudying, state.material.data, dispatch]);

  useEffect(() => {
    if (state.isStudying && documentId && isReady) {
      let isMounted = true;
      const controller = new AbortController();
      
      async function hydrate() {
        const currentRequestId = crypto.randomUUID();
        dispatch({ type: "START_HYDRATION", payload: { requestId: currentRequestId } });
        try {
          const data = await serviceProvider.getProvider().study.generateMaterial({
            topicId: documentId as string,
            signal: controller.signal
          });
          if (isMounted) {
            dispatch({ type: "START_STUDY", payload: { status: "ready", data, error: null, requestId: currentRequestId } });
          }
        } catch (err: unknown) {
          if (isMounted) {
            if (err instanceof Error && err.name === "AbortError") return;
            dispatch({ type: "START_STUDY", payload: { status: "error", data: null, error: err as Error, requestId: currentRequestId } });
          }
        }
      }
      
      hydrate();
      return () => {
        isMounted = false;
        controller.abort();
      };
    }
    
  }, [state.isStudying, dispatch, documentId]);

  const [isTutorOpen, setIsTutorOpen] = useState(false);
  const [initialTutorQuery, setInitialTutorQuery] = useState<string | undefined>(undefined);

  // If there's a selectedContext (e.g. from PDF selection), open Tutor automatically
  useEffect(() => {
    if (memory.study?.selectedContext) {
      setIsTutorOpen(true);
      setInitialTutorQuery(memory.study.selectedContext);
      
      // Consume the context so it doesn't trigger again on remounts
      if (remember) {
        remember('study', { ...memory.study, selectedContext: undefined });
      }
    }
  }, [memory.study?.selectedContext, remember, memory.study]);

  if (!state.isStudying || !documentId) {
    return (
      <StudySurface>
        <StudyEmptyState />
      </StudySurface>
    );
  }

  if (activeDoc && activeDoc.status !== "Ready") {
    return (
      <StudySurface>
        <ProcessingState status={activeDoc.status} />
      </StudySurface>
    );
  }

  if (state.material.status === "loading") {
    return (
      <StudySurface>
        <div className="flex-1 flex items-center justify-center h-full">
          <p className="text-secondary text-lg">Preparing study material...</p>
        </div>
      </StudySurface>
    );
  }

  if (state.material.status === "error") {
    return (
      <StudySurface>
        <div className="flex-1 flex items-center justify-center h-full">
          <p className="text-secondary text-lg">Unable to generate study material right now.</p>
        </div>
      </StudySurface>
    );
  }

  if (!state.material.data) return null;

  return (
    <StudySurface>
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={() => setIsTutorOpen(!isTutorOpen)}
          className="px-4 py-2 rounded-xs border border-line bg-surface text-ink hover:bg-raised transition-colors font-medium shadow-panel"
        >
          {isTutorOpen ? "Close Tutor" : "Ask AI Tutor"}
        </button>
      </div>

      <div className="flex w-full h-full">
        {/* Left Panel: The Learning Context */}
        <div className="w-64 flex-shrink-0 pt-12 pr-8 hidden md:block">
          <StudyContextPanel concept={state.material.data.concept} />
        </div>

        {/* Center Canvas: The Learning Content */}
        <div className="flex-1 flex flex-col pt-12 max-w-3xl relative">
          <StudyTimeline activeMode={state.activeMode} />
          
          <div className="flex-1 mt-12 pb-32">
            <StudyPerspective state={state} />
          </div>

          {/* Bottom Fixed Navigator */}
          <div className="fixed bottom-0 left-0 right-0 py-6 bg-gradient-to-t from-canvas via-canvas to-transparent flex justify-center pointer-events-none">
            <div className="w-full max-w-5xl px-6 lg:px-12 flex justify-end md:justify-center md:pl-64 pointer-events-auto">
              <StudyNavigator />
            </div>
          </div>
        </div>

        {/* Right Panel: The Tutor */}
        {isTutorOpen && documentId && (
          <div className="w-96 flex-shrink-0 h-full border-l border-line bg-surface shadow-overlay">
            <TutorChatPanel 
              documentId={documentId} 
              onClose={() => setIsTutorOpen(false)} 
              initialQuery={initialTutorQuery}
            />
          </div>
        )}
      </div>
    </StudySurface>
  );
}

export function StudyEnvironment() {
  return (
    <StudyProvider>
      <StudyEnvironmentBody />
    </StudyProvider>
  );
}
