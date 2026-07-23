"use client";

import { motion } from "framer-motion";
import type { SearchFinding } from "@/app/workspace/environments/search/SearchTypes";


interface SearchInspectorProps {
  finding: SearchFinding;
}

export function SearchInspector({ finding }: SearchInspectorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="flex flex-col gap-8 mt-2 overflow-hidden"
    >
      
      <div className="flex flex-col gap-6 pl-4 border-l-2 border-transparent">
        <div className="flex flex-col gap-2">
          <h4 className="text-xs uppercase tracking-widest font-medium text-ink/40">
            Why this was retrieved
          </h4>
          <p className="text-sm text-ink/70 leading-relaxed max-w-2xl">
            {finding.relevanceExplanation}
          </p>
        </div>

        <div className="flex flex-col gap-2">
          <h4 className="text-xs uppercase tracking-widest font-medium text-ink/40">
            Related Concepts
          </h4>
          <div className="flex flex-wrap gap-2">
            {finding.relatedConcepts.map((concept) => (
              <span
                key={concept}
                className="text-xs font-mono px-2 py-1 bg-ink/[0.03] text-ink/70 rounded-sm"
              >
                {concept}
              </span>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2 pt-2">
          <button className="w-fit text-sm font-medium text-ink hover:text-accent transition-colors outline-none">
            Open Originating Document →
          </button>
        </div>
      </div>
    </motion.div>
  );
}
