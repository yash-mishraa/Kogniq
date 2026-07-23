"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import type { NotebookState, NotebookAction } from "./NotebookTypes";
import { initialNotebookState, notebookReducer } from "./NotebookState";

interface NotebookContextValue {
  state: NotebookState;
  dispatch: React.Dispatch<NotebookAction>;
}

const NotebookContext = createContext<NotebookContextValue | null>(null);

export function NotebookProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(notebookReducer, initialNotebookState);

  return (
    <NotebookContext.Provider value={{ state, dispatch }}>
      {children}
    </NotebookContext.Provider>
  );
}

export function useNotebook() {
  const context = useContext(NotebookContext);
  if (!context) {
    throw new Error("useNotebook must be used within a NotebookProvider");
  }
  return context;
}
