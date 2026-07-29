"use client";

import { useDocuments, DocumentsProvider } from "./DocumentsContext";
import { DocumentSurface, DocumentCollection, DocumentEmptyState } from "@/components/documents";
import { ReadingSurface } from "@/components/workspace/ReadingSurface";
import { AnimatePresence } from "framer-motion";

import { useEffect } from "react";
import { serviceProvider } from "@/lib/providers";
import { useWorkspace } from "../../WorkspaceContext";

function DocumentsEnvironmentBody() {
  const { state, dispatch } = useDocuments();
  const { documents, activeDocumentId } = state;
  const activeDocument = documents.data?.find((doc) => doc.id === activeDocumentId);

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    
    async function hydrate() {
      const currentRequestId = crypto.randomUUID();
      dispatch({ type: "START_HYDRATION", payload: { requestId: currentRequestId } });
      try {
        const data = await serviceProvider.getProvider().documents.getDocuments(controller.signal);
        if (isMounted) {
          dispatch({ type: "SET_DOCUMENTS", payload: { status: "ready", data, error: null, requestId: currentRequestId } });
        }
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error && err.name === "AbortError") return;
          dispatch({ type: "SET_DOCUMENTS", payload: { status: "error", data: null, error: err as Error, requestId: currentRequestId } });
        }
      }
    }
    
    hydrate();
    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [dispatch]);

  // Polling for pending documents
  useEffect(() => {
    const terminalStates = ["Ready", "Failed", "Persisted"];
    const hasPendingDocs = documents.data?.some(doc => !terminalStates.includes(doc.status));
    
    if (!hasPendingDocs) return;

    let isMounted = true;
    const interval = setInterval(async () => {
      try {
        const data = await serviceProvider.getProvider().documents.getDocuments();
        if (isMounted) {
          dispatch({ type: "SET_DOCUMENTS", payload: { status: "ready", data, error: null, requestId: crypto.randomUUID() } });
        }
      } catch {
        // Silently fail polling
      }
    }, 2000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [documents.data, dispatch]);

  const { remember } = useWorkspace();

  // Automatically select the first document if none is selected
  useEffect(() => {
    if (documents.data && documents.data.length > 0 && !activeDocumentId) {
      const firstDoc = documents.data[0];
      dispatch({ type: "SELECT_DOCUMENT", payload: firstDoc.id });
      remember("documents", { openedDocument: firstDoc.id });
    }
  }, [documents.data, activeDocumentId, dispatch, remember]);

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
            status={activeDocument.status}
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
