"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { SearchFinding } from "@/app/workspace/environments/search/SearchTypes";
import { SearchInspector } from "./SearchInspector";
import { SearchEvidence } from "./SearchEvidence";

interface SearchFindingItemProps {
  finding: SearchFinding;
  isActive: boolean;
  isCondensed: boolean;
  onClick: () => void;
}

export function SearchFindingItem({ finding, isActive, isCondensed, onClick }: SearchFindingItemProps) {
  return (
    <motion.li
      layout
      className={`relative transition-opacity duration-500 ${
        isCondensed && !isActive ? "opacity-30 hover:opacity-70" : "opacity-100"
      }`}
    >
      <button
        onClick={onClick}
        className="w-full text-left flex flex-col gap-4 py-6 outline-none cursor-pointer group"
      >
        <SearchEvidence evidence={finding.evidence} />
        
        <div className="flex flex-col gap-1 pl-4 border-l-2 border-transparent">
          <h3 className={`font-serif tracking-tight transition-all duration-300 ${
            isActive ? "text-xl text-ink" : "text-lg text-ink/80 group-hover:text-ink"
          }`}>
            {finding.title}
          </h3>
        </div>
      </button>
      
      <AnimatePresence>
        {isActive && <SearchInspector finding={finding} />}
      </AnimatePresence>
    </motion.li>
  );
}
