"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import type { StudyState, StudyAction } from "./StudyTypes";
import { initialStudyState, studyReducer } from "./StudyState";

interface StudyContextValue {
  state: StudyState;
  dispatch: React.Dispatch<StudyAction>;
}

const StudyContext = createContext<StudyContextValue | null>(null);

export function StudyProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(studyReducer, initialStudyState);

  return (
    <StudyContext.Provider value={{ state, dispatch }}>
      {children}
    </StudyContext.Provider>
  );
}

export function useStudy() {
  const context = useContext(StudyContext);
  if (!context) {
    throw new Error("useStudy must be used within a StudyProvider");
  }
  return context;
}
