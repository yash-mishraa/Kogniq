"use client";

import { useEffect } from "react";
import { useWorkspace } from "../../WorkspaceContext";
import { QuizProvider, useQuiz } from "./QuizContext";
import { QuizEmptyState, QuizErrorState, QuizLoadingState, QuizNavigator, QuizQuestion, QuizResults, QuizSurface } from "@/components/quiz";
import { serviceProvider } from "@/lib/providers";

function QuizEnvironmentBody() {
  const { memory } = useWorkspace();
  const { state, dispatch } = useQuiz();
  const documentId = memory.documents?.openedDocument;

  useEffect(() => {
    if (!documentId) {
      dispatch({ type: "RESET" });
      return;
    }
    const controller = new AbortController();
    const requestId = crypto.randomUUID();
    dispatch({ type: "LOAD_STARTED", payload: { documentId, requestId } });
    void serviceProvider.getProvider().quiz.getQuiz({ documentId, signal: controller.signal }).then((questions) => {
      if (questions.length) dispatch({ type: "LOAD_SUCCEEDED", payload: { documentId, requestId, questions } });
      else dispatch({ type: "LOAD_EMPTY", payload: { documentId, requestId } });
    }).catch((error: unknown) => {
      if (error instanceof DOMException && error.name === "AbortError") return;
      dispatch({ type: "LOAD_FAILED", payload: { documentId, requestId, error: error instanceof Error ? error : new Error("Unable to load quiz.") } });
    });
    return () => controller.abort();
  }, [documentId, dispatch]);

  return <QuizSurface>{state.status === "loading" ? <QuizLoadingState /> : state.status === "error" ? <QuizErrorState error={state.error} /> : state.status === "empty" || state.status === "idle" ? <QuizEmptyState hasDocument={Boolean(documentId)} /> : state.status === "completed" ? <QuizResults /> : <><QuizQuestion /><QuizNavigator /></>}</QuizSurface>;
}

export function QuizEnvironment() {
  return <QuizProvider><QuizEnvironmentBody /></QuizProvider>;
}
