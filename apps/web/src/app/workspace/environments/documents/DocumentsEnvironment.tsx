"use client";

import { useDocuments, DocumentsProvider } from "./DocumentsContext";
import { DocumentSurface, DocumentCollection, DocumentEmptyState } from "@/components/documents";
import { ReadingSurface } from "@/components/workspace/ReadingSurface";
import { AnimatePresence } from "framer-motion";

import { useEffect } from "react";
import { serviceProvider } from "@/lib/providers";

function DocumentsEnvironmentBody() {
  const { state, dispatch } = useDocuments();
  const { documents, activeDocumentId } = state;
  const activeDocument = documents.data?.find((doc) => doc.id === activeDocumentId);

  useEffect(() => {
    if (documents.status !== "idle") return;
    
    const controller = new AbortController();
    
    async function hydrate() {
      dispatch({ type: "SET_DOCUMENTS", payload: { ...documents, status: "loading" } });
      try {
        const data = await serviceProvider.getProvider().documents.getDocuments(controller.signal);
        dispatch({ type: "SET_DOCUMENTS", payload: { status: "ready", data, error: null } });
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") return;
        dispatch({ type: "SET_DOCUMENTS", payload: { status: "error", data: null, error: err as Error } });
      }
    }
    
    hydrate();
    return () => controller.abort();
  }, [documents.status, dispatch, documents]);

  if (documents.status === "loading") {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-secondary text-lg">Retrieving documents...</p>
      </div>
    );
  }

  if (documents.status === "error") {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-secondary text-lg">Unable to retrieve documents right now.</p>
      </div>
    );
  }

  if (!documents.data || documents.data.length === 0) {
    return <DocumentEmptyState />;
  }

  return (
    <DocumentSurface>
      <DocumentCollection />
      <AnimatePresence>
        {activeDocument && (
          <ReadingSurface 
            key={activeDocument.id}
            layoutId={`title-${activeDocument.id}`}
            title={activeDocument.title}
            content={activeDocument.content} 
          />
        )}
      </AnimatePresence>
    </DocumentSurface>
  );
}

export function DocumentsEnvironment() {
  return (
    <DocumentsProvider>
      <DocumentsEnvironmentBody />
    </DocumentsProvider>
  );
}
