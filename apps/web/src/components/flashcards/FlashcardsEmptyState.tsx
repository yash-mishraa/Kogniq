"use client";

import { useWorkspace } from "@/app/workspace/WorkspaceContext";

export function FlashcardsEmptyState() {
  const { memory } = useWorkspace();
  const documentId = memory.documents?.openedDocument;

  return (
    <div className="flex-1 flex flex-col items-center justify-center h-full text-center max-w-lg mx-auto">
      <div className="w-16 h-16 bg-secondary/10 text-tertiary rounded-2xl flex items-center justify-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
      </div>
      <h3 className="text-xl font-medium text-primary mb-2">No Flashcards Available</h3>
      {documentId ? (
        <p className="text-secondary">
          There are no flashcards generated for the current document. If the document was just uploaded, generation may still be in progress, or it may not contain suitable content.
        </p>
      ) : (
        <p className="text-secondary">
          Select a document from the Documents workspace to begin reviewing its flashcards.
        </p>
      )}
    </div>
  );
}
