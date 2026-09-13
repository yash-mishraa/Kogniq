"use client";

import { useEffect, useState, useRef } from "react";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";
import { useStudio } from "@/app/workspace/environments/studio/StudioContext";
import ReactMarkdown from "react-markdown";

export function StudioEditor() {
  const { state, dispatch } = useStudio();
  const { isPreview } = state;
  const { memory, remember } = useWorkspace();
  const documentId = memory.documents?.openedDocument;

  // Local state for fast typing
  const initialDraft = (documentId && memory.studio?.studioDrafts?.[documentId]) || "";
  const [draft, setDraft] = useState(initialDraft);
  
  // Track memory and draft without causing updates
  const memoryRef = useRef(memory);
  useEffect(() => {
    memoryRef.current = memory;
  }, [memory]);
  
  const draftRef = useRef(draft);
  useEffect(() => {
    draftRef.current = draft;
  }, [draft]);

  // Handle document switching: reset local draft to the newly opened document's draft
  useEffect(() => {
    if (documentId) {
      setDraft(memory.studio?.studioDrafts?.[documentId] || "");
    } else {
      setDraft("");
    }
    // We purposefully do NOT depend on memory.studioDrafts entirely to avoid cyclic updates
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documentId]);

  // Debounced auto-save
  useEffect(() => {
    if (!documentId) return;

    const timer = setTimeout(() => {
      remember("studio", {
        studioDrafts: {
          ...(memoryRef.current.studio?.studioDrafts || {}),
          [documentId]: draft,
        }
      });
    }, 500);

    return () => clearTimeout(timer);
  }, [draft, documentId, remember]);

  // Flush on unmount
  useEffect(() => {
    return () => {
      if (documentId) {
        // Synchronously save the latest ref on unmount using latest memory
        remember("studio", {
          studioDrafts: {
            ...(memoryRef.current.studio?.studioDrafts || {}),
            [documentId]: draftRef.current,
          }
        });
      }
    };
  }, [documentId, remember]);

  const handleExport = () => {
    if (!documentId) return;
    const blob = new Blob([draft], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `kogniq-draft-${documentId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!documentId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center h-full">
        <h2 className="text-xl font-medium text-ink mb-2">No Document Selected</h2>
        <p className="text-secondary text-sm">Please select a document from the Documents environment first.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-paper">
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-8 border-b border-ink/5 shrink-0">
        <div className="flex items-center gap-4 bg-paper-subtle p-1 rounded-md border border-ink/10">
          <button
            onClick={() => dispatch({ type: "SET_PREVIEW", payload: false })}
            className={`px-4 py-1.5 text-sm font-medium rounded transition-colors ${!isPreview ? "bg-paper text-ink shadow-sm" : "text-secondary hover:text-ink"}`}
          >
            Edit
          </button>
          <button
            onClick={() => dispatch({ type: "SET_PREVIEW", payload: true })}
            className={`px-4 py-1.5 text-sm font-medium rounded transition-colors ${isPreview ? "bg-paper text-ink shadow-sm" : "text-secondary hover:text-ink"}`}
          >
            Preview
          </button>
        </div>
        
        <button
          onClick={handleExport}
          className="text-sm font-medium text-ink/70 hover:text-ink px-4 py-2 rounded border border-ink/10 hover:border-ink/20 transition-colors"
        >
          Export .md
        </button>
      </div>

      {/* Editor / Preview Area */}
      <div className="flex-1 overflow-y-auto relative">
        {!isPreview ? (
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Develop a thought..."
            className="w-full h-full p-8 md:p-12 resize-none bg-transparent outline-none text-lg font-serif text-ink/90 placeholder:text-ink/30 leading-relaxed"
            spellCheck={false}
          />
        ) : (
          <div className="p-8 md:p-12 h-full">
            <div className="prose prose-lg prose-headings:font-serif prose-headings:font-normal prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-sm prose-h3:font-mono prose-h3:uppercase prose-h3:tracking-widest prose-h3:text-ink/40 prose-p:font-serif prose-p:text-xl prose-p:leading-relaxed prose-p:text-ink/90 prose-li:font-serif prose-li:text-lg prose-li:leading-relaxed prose-li:text-ink/80 text-ink max-w-none">
              <ReactMarkdown>{draft || "*No content to preview.*"}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
