"use client";

import { useDocuments } from "@/app/workspace/environments/documents/DocumentsContext";
import { DocumentItem } from "./DocumentItem";
import { motion, AnimatePresence } from "framer-motion";
import { useDocumentUpload } from "./useDocumentUpload";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

export function DocumentCollection() {
  const { state, dispatch } = useDocuments();
  const { documents, activeDocumentId } = state;
  const hasActiveDocument = activeDocumentId !== null;
  const { fileInputRef, triggerUpload, handleFileChange } = useDocumentUpload();

  const [headerTarget, setHeaderTarget] = useState<HTMLElement | null>(null);

  useEffect(() => {
    setHeaderTarget(document.getElementById("workspace-header-action"));
  }, []);

  return (
    <motion.div
      layout
      className="flex flex-col flex-shrink-0 overflow-y-auto transition-all duration-500 w-full pt-12 px-6 lg:px-12 bg-transparent"
    >
      <input
        type="file"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,.md,.txt,.doc,.docx"
      />
      {headerTarget && createPortal(
        <button
          type="button"
          onClick={triggerUpload}
          className="text-[clamp(0.85rem,1.5vw,1rem)] font-medium tracking-wide text-ink/70 hover:text-accent transition-colors outline-none"
        >
          + Upload Document
        </button>,
        headerTarget
      )}
      {!hasActiveDocument && (
        <motion.div layout className="mb-8">
          <h2 className="text-xl font-serif text-ink tracking-tight">Knowledge Base</h2>
        </motion.div>
      )}
      <ul className="flex flex-col gap-1 pb-24">
        <AnimatePresence initial={false}>
          {documents.data && documents.data.map((doc) => {
            const isActive = activeDocumentId === doc.id;

            // When a document is active, we might still show other documents but subdued,
            // or we might hide them. Let's show them as a condensed list.
            if (isActive) return null;

            return (
              <DocumentItem
                key={doc.id}
                document={doc}
                isCondensed={hasActiveDocument}
                onClick={() => {
                  if (isActive) {
                    dispatch({ type: "SELECT_DOCUMENT", payload: null });
                  } else {
                    dispatch({ type: "SELECT_DOCUMENT", payload: doc.id });
                  }
                }}
              />
            );
          })}
        </AnimatePresence>
      </ul>
    </motion.div>
  );
}
