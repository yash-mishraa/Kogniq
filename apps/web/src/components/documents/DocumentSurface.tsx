"use client";

import type { ReactNode } from "react";
import { useDocuments } from "@/app/workspace/environments/documents/DocumentsContext";
import { motion } from "framer-motion";

export function DocumentSurface({ children }: { children: ReactNode }) {
  const { state } = useDocuments();
  const hasActiveDocument = state.activeDocumentId !== null;

  return (
    <div className="flex flex-1 w-full h-full relative overflow-hidden bg-[#fafafa]">
      <motion.div
        layout
        className={`flex w-full h-full transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${
          hasActiveDocument ? "flex-row" : "flex-col max-w-5xl mx-auto"
        }`}
      >
        {children}
      </motion.div>
    </div>
  );
}
