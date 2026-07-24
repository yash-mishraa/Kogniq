"use client";

import { motion } from "framer-motion";
import { type ReactNode } from "react";

export interface ReadingSurfaceProps {
  title: string;
  layoutId?: string;
  content?: ReactNode;
  status?: string;
}

export function ReadingSurface({ title, layoutId, content, status }: ReadingSurfaceProps) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="flex-1 flex flex-col bg-white overflow-y-auto px-16 lg:px-32 py-24"
      style={{
        boxShadow: "-12px 0 32px rgba(0, 0, 0, 0.02)",
      }}
    >
      <div className="max-w-[680px] mx-auto w-full">
        <motion.h1 
          layoutId={layoutId}
          className="text-4xl font-serif text-ink mb-12 tracking-tight leading-[1.15]"
        >
          {title}
        </motion.h1>
        
        <div className="prose prose-lg prose-ink max-w-none">
          {content ? (
            <div className="text-ink/80 leading-relaxed space-y-8">
              {content}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 opacity-50 space-y-2">
              <span className="font-serif italic text-lg tracking-wide">
                {status === "Ready" || status === "Persisted"
                  ? "Document successfully processed and stored."
                  : "Extracting text..."}
              </span>
              {(status === "Ready" || status === "Persisted") && (
                <span className="text-sm">
                  (Full document rendering will arrive in a future phase)
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.article>
  );
}
