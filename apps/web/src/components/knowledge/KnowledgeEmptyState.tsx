"use client";

import { motion } from "framer-motion";

export function KnowledgeEmptyState() {
  return (
    <div className="absolute inset-0 flex items-center justify-center p-12 pointer-events-none">
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full flex flex-col gap-6 items-center text-center"
      >
        <p className="text-lg font-serif text-ink/60 leading-relaxed">
          Select a document from the Documents workspace to explore its knowledge graph.
        </p>
      </motion.div>
    </div>
  );
}
