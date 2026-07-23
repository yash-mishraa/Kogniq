"use client";

import { useStudy } from "@/app/workspace/environments/study/StudyContext";


export function StudyNavigator() {
  const { state, dispatch } = useStudy();

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
    } else {
      nextAction = {
        label: "Finish Study Session",
        onClick: () => dispatch({ type: "END_STUDY" }),
      };
    }
  }

  return (
    <div className="flex justify-end pointer-events-auto">
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
