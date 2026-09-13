"use client";

import { useEffect, useRef } from "react";
import { useWorkspace } from "../../WorkspaceContext";
import { QuizProvider, useQuiz } from "./QuizContext";
import { quizScore } from "./QuizState";
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

  const isSynced = useRef(false);
  useEffect(() => {
    if (state.status === "completed" && state.documentId && state.requestId && !isSynced.current) {
      isSynced.current = true;
      const score = quizScore(state);
      const total_questions = state.questions.length;
      
      serviceProvider.getProvider().analytics.recordEvent({
        event_id: state.requestId,
        event_type: "quiz_completed",
        document_id: state.documentId,
        data: { score, total_questions }
      }).catch(err => console.error("Failed to record analytics", err));
    }
    if (state.status !== "completed") {
        isSynced.current = false;
    }
  }, [state.status, state.documentId, state.requestId, state.questions.length, state]);

  return <QuizSurface>{state.status === "loading" ? <QuizLoadingState /> : state.status === "error" ? <QuizErrorState error={state.error} /> : state.status === "empty" || state.status === "idle" ? <QuizEmptyState hasDocument={Boolean(documentId)} /> : state.status === "completed" ? <QuizResults /> : <><QuizQuestion /><QuizNavigator /></>}</QuizSurface>;
}

export function QuizEnvironment() {
  return <QuizProvider><QuizEnvironmentBody /></QuizProvider>;
}
