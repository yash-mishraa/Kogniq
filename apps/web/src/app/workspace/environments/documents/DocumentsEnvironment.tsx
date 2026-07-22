"use client";

import { useDocuments, DocumentsProvider } from "./DocumentsContext";
import { DocumentSurface, DocumentCollection, DocumentEmptyState } from "@/components/documents";
import { ReadingSurface } from "@/components/workspace/ReadingSurface";
import { AnimatePresence } from "framer-motion";

function DocumentsEnvironmentBody() {
  const { state } = useDocuments();
  const { documents, activeDocumentId } = state;
  const activeDocument = documents.find((doc) => doc.id === activeDocumentId);

  if (documents.length === 0) {
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
