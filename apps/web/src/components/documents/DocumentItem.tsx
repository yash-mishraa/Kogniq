"use client";

import { motion } from "framer-motion";
import type { DocumentItem as DocumentItemType } from "@/app/workspace/environments/documents/DocumentsTypes";
import { DocumentMetadata } from "./DocumentMetadata";
import { DocumentLifecycle } from "./DocumentLifecycle";

interface DocumentItemProps {
  document: DocumentItemType;
  isCondensed: boolean;
  onClick: () => void;
  onDelete?: (id: string) => void;
}

export function DocumentItem({ document, isCondensed, onClick, onDelete }: DocumentItemProps) {
  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className={`relative ${isCondensed ? "opacity-40 hover:opacity-100" : "opacity-100"}`} // quiet index when one is selected
    >
      <div className="flex justify-between items-start">
        <button
          onClick={onClick}
          className="flex-1 text-left flex flex-col gap-2 py-5 outline-none transition-opacity duration-300 cursor-pointer hover:opacity-70"
        >
          <div className="flex flex-col gap-2">
            <motion.h3 
              layoutId={`title-${document.id}`}
              className="font-serif text-ink tracking-tight text-2xl leading-snug"
            >
              {document.title}
            </motion.h3>
            
            <DocumentLifecycle status={document.status} />
          </div>

          <motion.div layout="position">
            <DocumentMetadata document={document} />
          </motion.div>
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (onDelete) onDelete(document.id);
          }}
          className="mt-6 text-sm font-mono text-danger/60 hover:text-danger uppercase tracking-widest transition-colors outline-none"
        >
          Delete
        </button>
      </div>
      
      {/* Editorial divider */}
      <div className="w-full h-px bg-black/5 mt-2" />
    </motion.li>
  );
}
