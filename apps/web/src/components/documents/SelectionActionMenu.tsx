/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState, useRef, useEffect } from "react";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";
import { TutorFlashcardProposal, TutorNoteProposal } from "@/app/workspace/environments/study/TutorChatPanel";
import { motion, AnimatePresence } from "framer-motion";

export interface SelectionContext {
  documentId: string;
  pageNumber: number;
  selectedText: string;
  surroundingContext?: string;
  x: number;
  y: number;
  timestamp: number;
}

interface SelectionActionMenuProps {
  selection: SelectionContext;
  onClose: () => void;
}

export function SelectionActionMenu({ selection, onClose }: SelectionActionMenuProps) {
  const { switchEnvironment, remember, memory } = useWorkspace();
  const [activeAction, setActiveAction] = useState<"explain" | "flashcard" | "note" | null>(null);
  const [actionStatus, setActionStatus] = useState<"loading" | "error" | "success" | null>(null);
  const [resultData, setResultData] = useState<any>(null);

  const menuRef = useRef<HTMLDivElement>(null);

  // Handle clicking outside to close
  useEffect(() => {
    const handlePointerDown = (e: PointerEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    // small delay so we don't catch the pointerup that triggered this
    setTimeout(() => {
      document.addEventListener("pointerdown", handlePointerDown);
    }, 50);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
    };
  }, [onClose]);

  const invokeAction = async (action: "explain" | "flashcard" | "note") => {
    setActiveAction(action);
    setActionStatus("loading");

    try {
      let instruction = "";
      if (action === "explain") {
        instruction = `Explain the following text from page ${selection.pageNumber} in a concise, easily understandable way:\n\n<selected_document_text>\n${selection.selectedText}\n</selected_document_text>`;
      } else if (action === "flashcard") {
        instruction = `Create a flashcard covering the core concept from this text on page ${selection.pageNumber}:\n\n<selected_document_text>\n${selection.selectedText}\n</selected_document_text>\n\nUse your flashcard tool.`;
      } else if (action === "note") {
        instruction = `Create a brief summary note for my notebook based on this text from page ${selection.pageNumber}:\n\n<selected_document_text>\n${selection.selectedText}\n</selected_document_text>\n\nUse your note tool.`;
      }

      if (selection.surroundingContext) {
        instruction += `\n\nFor additional context, here is the surrounding text on the page:\n<surrounding_context>\n${selection.surroundingContext}\n</surrounding_context>`;
      }

      const token = localStorage.getItem("token") || "demo-user-1";
      
      // If there's an active session in this tab, append to it so it's not orphaned.
      const activeSessionId = sessionStorage.getItem("activeTutorSessionId");
      const payload: any = {
        document_id: selection.documentId,
        messages: [{ role: "user", content: instruction }]
      };
      if (activeSessionId) {
        payload.session_id = activeSessionId;
      }

      const response = await fetch("/api/v1/agent/tutor/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error("Failed to process action");
      }

      const data = await response.json();
      
      if (data.session_id) {
        sessionStorage.setItem("activeTutorSessionId", data.session_id);
      }
      
      let parsedToolEvent = null;
      if (data.tool_events && data.tool_events.length > 0) {
        for (const event of data.tool_events) {
          try {
            const parsed = JSON.parse(event);
            if ((action === "flashcard" && parsed.type === "flashcard_proposal") ||
                (action === "note" && parsed.type === "note_proposal")) {
              parsedToolEvent = parsed;
              break;
            }
          } catch {}
        }
      }

      setResultData({
        textResponse: data.content,
        toolEvent: parsedToolEvent
      });
      setActionStatus("success");

    } catch (err) {
      setActionStatus("error");
    }
  };

  const handleAskTutor = () => {
    // Open Tutor chat with context pre-filled
    const initialQuery = `I'm looking at page ${selection.pageNumber}. I have a question about this part:\n\n<selected_document_text>\n${selection.selectedText}\n</selected_document_text>`;
    remember("study", { ...memory.study, selectedContext: initialQuery });
    switchEnvironment("study");
    onClose();
  };

  return (
    <AnimatePresence>
      <motion.div
        ref={menuRef}
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="fixed z-50 bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden"
        style={{
          left: Math.max(16, selection.x - 150),
          top: Math.max(16, selection.y + 24),
          width: activeAction ? 350 : 'auto',
          maxWidth: '90vw'
        }}
      >
        {!activeAction ? (
          <div className="flex p-1 space-x-1">
            <button 
              onClick={handleAskTutor}
              className="px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors whitespace-nowrap"
            >
              Ask Tutor
            </button>
            <div className="w-px bg-gray-200 my-1" />
            <button 
              onClick={() => invokeAction("explain")}
              className="px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors whitespace-nowrap"
            >
              Explain
            </button>
            <button 
              onClick={() => invokeAction("flashcard")}
              className="px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors whitespace-nowrap"
            >
              Flashcard
            </button>
            <button 
              onClick={() => invokeAction("note")}
              className="px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors whitespace-nowrap"
            >
              Save Note
            </button>
          </div>
        ) : (
          <div className="p-4 max-h-[400px] overflow-y-auto">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-gray-800 capitalize">{activeAction}</h3>
              <button onClick={onClose} className="text-gray-400 hover:text-gray-600">×</button>
            </div>

            {actionStatus === "loading" && (
              <div className="flex items-center space-x-3 text-gray-500 py-4">
                <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                <span className="text-sm italic">
                  {activeAction === "explain" ? "Explaining selection..." : 
                   activeAction === "flashcard" ? "Preparing flashcard..." : 
                   "Preparing note..."}
                </span>
              </div>
            )}

            {actionStatus === "error" && (
              <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
                Failed to process your request. Please try again.
                <button onClick={() => invokeAction(activeAction)} className="mt-2 text-xs font-semibold underline block">Retry</button>
              </div>
            )}

            {actionStatus === "success" && resultData && (
              <div className="space-y-4">
                {activeAction === "explain" && (
                  <div className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-md border border-gray-100">
                    {resultData.textResponse}
                  </div>
                )}
                
                {activeAction === "flashcard" && resultData.toolEvent && (
                  <TutorFlashcardProposal proposal={resultData.toolEvent} documentId={selection.documentId} />
                )}

                {activeAction === "note" && resultData.toolEvent && (
                  <TutorNoteProposal proposal={resultData.toolEvent} documentId={selection.documentId} />
                )}

                {/* Fallback if tool call failed but text returned */}
                {activeAction !== "explain" && !resultData.toolEvent && (
                  <div className="text-sm text-gray-700">
                    {resultData.textResponse}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
