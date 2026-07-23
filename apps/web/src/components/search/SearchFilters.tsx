"use client";

import { motion } from "framer-motion";
import type { SearchFilter } from "@/app/workspace/environments/search/SearchTypes";

interface SearchFiltersProps {
  activeFilter: SearchFilter;
  onFilterChange: (filter: SearchFilter) => void;
}

const FILTERS: { value: SearchFilter; label: string }[] = [
  { value: "all", label: "All Knowledge" },
  { value: "documents", label: "Documents" },
  { value: "concepts", label: "Concepts" },
  { value: "learning", label: "Learning Material" },
];

export function SearchFilters({ activeFilter, onFilterChange }: SearchFiltersProps) {
  return (
    <div className="flex flex-wrap gap-6 items-center">
      {FILTERS.map((f) => (
        <button
          key={f.value}
          onClick={() => onFilterChange(f.value)}
          className={`relative px-1 py-1 text-sm font-medium transition-colors outline-none ${
            activeFilter === f.value ? "text-ink" : "text-ink/40 hover:text-ink/70"
          }`}
        >
          {f.label}
          {activeFilter === f.value && (
            <motion.div
              layoutId="active-filter-indicator"
              className="absolute -bottom-1 left-0 right-0 h-[1px] bg-ink"
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            />
          )}
        </button>
      ))}
    </div>
  );
}
