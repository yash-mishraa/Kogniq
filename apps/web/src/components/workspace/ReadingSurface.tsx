"use client";

import { motion } from "framer-motion";
import { type ReactNode } from "react";

import { LearningHub } from "./LearningHub";

import { PDFReader } from "../documents/PDFReader";

export interface ReadingSurfaceProps {
  title: string;
  layoutId?: string;
  content?: ReactNode; // Kept for backward compatibility if needed in some paths, though PDFReader takes over
  status?: string;
}

export function ReadingSurface({ title, layoutId, content, status }: ReadingSurfaceProps) {
  // Extract document ID from layoutId (title-uuid)
  const documentId = layoutId?.replace("title-", "");

  const isReady = status === "Ready" || status === "Persisted";
  const isFailed = status === "Failed" || status === "Error";

  return (
    <motion.article
      layout
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="flex-1 flex flex-col bg-white overflow-hidden"
    >
      {!isReady ? (
        <div className="flex-1 flex flex-col items-center justify-center p-16 text-center">
          <motion.h1 
            layoutId={layoutId}
            className="text-4xl font-serif text-ink mb-12 tracking-tight leading-[1.15]"
          >
            {title}
          </motion.h1>
          <div className="max-w-[680px] w-full">
            <div className="flex flex-col items-center justify-center py-32 space-y-4">
              {isFailed ? (
                <>
                  <div className="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mb-2">
                    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <span className="font-serif italic text-lg tracking-wide text-red-600">
                    Failed to process document
                  </span>
                </>
              ) : (
                <>
                  <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin mb-2" />
                  <span className="font-serif italic text-lg tracking-wide opacity-70">
                    {status || "Loading..."}
                  </span>
                  <span className="text-sm opacity-50">
                    We are extracting text, chunks, and metadata...
                  </span>
                </>
              )}
            </div>
            {documentId && (
              <LearningHub documentId={documentId} status={status} />
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex-none px-6 py-4 bg-white border-b border-gray-100 flex items-center justify-between shadow-sm z-20">
            <motion.h1 
              layoutId={layoutId}
              className="text-lg font-medium text-ink truncate max-w-xl"
            >
              {title}
            </motion.h1>
            {documentId && (
              <div className="hidden lg:block">
                {/* 
                  Keep learning hub visually minimized or separated since the PDF takes priority. 
                  For now we can render a mini version or a button to open it.
                  Let's just hide the large inline learning hub in reader mode, 
                  because the Study (Tutor) environment handles interaction.
                */}
              </div>
            )}
          </div>
          
          {/* PDF Viewer */}
          <div className="flex-1 relative overflow-hidden">
            {documentId && <PDFReader key={documentId} documentId={documentId} />}
          </div>
        </div>
      )}
    </motion.article>
  );
}
