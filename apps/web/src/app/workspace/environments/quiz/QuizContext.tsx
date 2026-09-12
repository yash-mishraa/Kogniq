"use client";

import { createContext, useContext, useReducer, type Dispatch, type ReactNode } from "react";
import { initialQuizState, quizReducer } from "./QuizState";
import type { QuizAction, QuizState } from "./QuizTypes";

const QuizContext = createContext<{ state: QuizState; dispatch: Dispatch<QuizAction> } | null>(null);

export function QuizProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(quizReducer, initialQuizState);
  return <QuizContext.Provider value={{ state, dispatch }}>{children}</QuizContext.Provider>;
}

export function useQuiz() {
  const value = useContext(QuizContext);
  if (!value) throw new Error("useQuiz must be used within a QuizProvider.");
  return value;
}
