"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import { type LearningHubState, type LearningHubAction } from "./LearningHubTypes";
import { initialLearningHubState, learningHubReducer } from "./LearningHubState";

interface LearningHubContextValue {
  state: LearningHubState;
  dispatch: React.Dispatch<LearningHubAction>;
}

const LearningHubContext = createContext<LearningHubContextValue | undefined>(undefined);

export function LearningHubProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(learningHubReducer, initialLearningHubState);

  return (
    <LearningHubContext.Provider value={{ state, dispatch }}>
      {children}
    </LearningHubContext.Provider>
  );
}

export function useLearningHub() {
  const context = useContext(LearningHubContext);
  if (!context) {
    throw new Error("useLearningHub must be used within a LearningHubProvider");
  }
  return context;
}
