"use client";

import { useDocuments } from "@/app/workspace/environments/documents/DocumentsContext";
import { DocumentItem } from "./DocumentItem";
import { motion, AnimatePresence } from "framer-motion";

export function DocumentCollection() {
  const { state, dispatch } = useDocuments();
  const { documents, activeDocumentId } = state;
  const hasActiveDocument = activeDocumentId !== null;

  return (
    <motion.div
      layout
      className={`flex flex-col flex-shrink-0 overflow-y-auto transition-all duration-500 ${
        hasActiveDocument ? "w-[240px] xl:w-[280px] bg-transparent pt-12 px-6" : "w-full pt-12 px-6 lg:px-12 bg-transparent"
      }`}
    >
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
