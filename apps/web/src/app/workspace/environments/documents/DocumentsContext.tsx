"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import type { DocumentsState, DocumentsAction } from "./DocumentsTypes";
import { initialDocumentsState, documentsReducer } from "./DocumentsState";

interface DocumentsContextValue {
  state: DocumentsState;
  dispatch: React.Dispatch<DocumentsAction>;
}

const DocumentsContext = createContext<DocumentsContextValue | null>(null);

export function DocumentsProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(documentsReducer, initialDocumentsState);

  return (
    <DocumentsContext.Provider value={{ state, dispatch }}>
      {children}
    </DocumentsContext.Provider>
  );
}

export function useDocuments() {
  const context = useContext(DocumentsContext);
  if (!context) {
    throw new Error("useDocuments must be used within a DocumentsProvider");
  }
  return context;
}
