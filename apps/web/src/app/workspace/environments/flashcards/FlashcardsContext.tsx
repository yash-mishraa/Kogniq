"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import { type FlashcardsState, type FlashcardsAction } from "./FlashcardsTypes";
import { initialFlashcardsState, flashcardsReducer } from "./FlashcardsState";

interface FlashcardsContextValue {
  state: FlashcardsState;
  dispatch: React.Dispatch<FlashcardsAction>;
}

const FlashcardsContext = createContext<FlashcardsContextValue | null>(null);

export function FlashcardsProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(flashcardsReducer, initialFlashcardsState);

  return (
    <FlashcardsContext.Provider value={{ state, dispatch }}>
      {children}
    </FlashcardsContext.Provider>
  );
}

export function useFlashcards() {
  const value = useContext(FlashcardsContext);
  if (!value) {
    throw new Error("useFlashcards must be used within a FlashcardsProvider");
  }
  return value;
}
