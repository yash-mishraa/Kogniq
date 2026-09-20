"use client";

import { useStudy } from "@/app/workspace/environments/study/StudyContext";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";
import { serviceProvider } from "@/lib/providers";
import { useKnowledgeState } from "./useKnowledgeState";

export function StudyNavigator() {
  const { state, dispatch } = useStudy();
  const { memory, switchEnvironment } = useWorkspace();
  const documentId = memory.documents?.openedDocument;
  
  const { knowledgeState, isLoading, error } = useKnowledgeState(documentId || null);

  if (!state.isStudying || !state.material || !state.material.data) return null;

  const currentMode = state.activeMode;
  let nextAction: { label: string; onClick: () => void } | null = null;

  if (currentMode === "understand") {
    nextAction = {
      label: "Review Notes →",
      onClick: () => dispatch({ type: "SET_MODE", payload: "review" }),
    };
  } else if (currentMode === "review") {
    nextAction = {
      label: "Start Recall →",
      onClick: () => dispatch({ type: "SET_MODE", payload: "recall" }),
    };
  } else if (currentMode === "recall") {
    if (state.recallIndex < state.material.data.recall.length - 1) {
      nextAction = {
        label: "Next Concept →",
        onClick: () => dispatch({ type: "NEXT_RECALL" }),
      };
    } else {
      nextAction = {
        label: "Test Understanding →",
        onClick: () => dispatch({ type: "SET_MODE", payload: "test" }),
      };
    }
  } else if (currentMode === "test") {
    if (state.testIndex < state.material.data.test.length - 1) {
      nextAction = {
        label: "Next Question →",
        onClick: () => dispatch({ type: "NEXT_TEST" }),
      };
    } else if (!state.completed) {
      nextAction = {
        label: "Finish Study Session",
        onClick: () => {
          dispatch({ type: "MARK_COMPLETED" });
          
          const eventId = state.material.requestId || crypto.randomUUID();
          
          serviceProvider.getProvider().analytics.enqueueBatchEvent({
            event_id: eventId,
            event_type: "study_session_completed",
            resource_id: documentId!,
            data: {
              completed_at: new Date().toISOString()
            },
            idempotency_key: eventId
          });
        },
      };
    }
  }

  if (state.completed) {
    return (
      <div className="flex items-center gap-4 bg-canvas/80 backdrop-blur-md px-6 py-4 rounded-full border border-ink/10 shadow-lg">
        <p className="font-medium text-ink tracking-tight pr-2">Session Complete</p>
        <button
          type="button"
          onClick={() => {
            switchEnvironment("documents");
          }}
          className="px-6 py-2 bg-ink text-canvas rounded-full font-medium tracking-tight hover:bg-accent transition-colors"
        >
          Return to Workspace
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-4 justify-end pointer-events-auto">
      <div className="px-4 py-2 bg-canvas/80 backdrop-blur-md rounded-full border border-ink/10 text-sm font-medium tracking-tight text-ink/70">
        {isLoading && <span>Loading mastery...</span>}
        {!isLoading && error && <span>Mastery data unavailable</span>}
        {!isLoading && !error && !knowledgeState && <span>Mastery data unavailable</span>}
        {!isLoading && !error && knowledgeState && (
          <span>Mastery: {Math.round(knowledgeState.mastery_score * 100)}%</span>
        )}
      </div>

      {nextAction && (
        <button
          onClick={nextAction.onClick}
          className="px-6 py-3 bg-ink text-canvas font-mono text-sm uppercase tracking-widest hover:bg-ink/90 transition-colors shadow-lg outline-none"
        >
          {nextAction.label}
        </button>
      )}
    </div>
  );
}
