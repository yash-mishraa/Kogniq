"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { SearchFinding } from "@/app/workspace/environments/search/SearchTypes";
import { SearchInspector } from "./SearchInspector";

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
        className="w-full text-left flex flex-col gap-2 py-5 outline-none cursor-pointer group"
      >
        <div className="flex flex-col gap-1">
          <h3 className={`font-serif tracking-tight transition-all duration-300 ${
            isActive ? "text-3xl leading-snug text-ink" : "text-2xl leading-snug text-ink group-hover:text-ink/70"
          }`}>
            {finding.title}
          </h3>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-widest font-medium text-ink/30">
              {finding.documentId}
            </span>
          </div>
        </div>
      </button>
      
      <AnimatePresence>
        {isActive && <SearchInspector finding={finding} />}
      </AnimatePresence>
    </motion.li>
  );
}
