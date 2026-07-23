"use client";

import { useSearch } from "@/app/workspace/environments/search/SearchContext";
import { SearchFindingItem } from "./SearchFindingItem";
import { SearchFilters } from "./SearchFilters";
import { motion, AnimatePresence } from "framer-motion";

export function SearchFindings() {
  const { state, dispatch } = useSearch();
  const { findings, activeFindingId, activeFilter } = state;

  const hasActiveFinding = activeFindingId !== null;

  return (
    <motion.div
      layout
      className="flex flex-col flex-shrink-0 overflow-y-auto transition-all duration-500 w-full"
    >
      <div className="mb-12 flex flex-col gap-6">
        <h2 className="text-xl font-serif text-ink tracking-tight">
          Findings for &quot;{state.query}&quot;
        </h2>
        <SearchFilters activeFilter={activeFilter} onFilterChange={(f) => dispatch({ type: "SET_FILTER", payload: f })} />
      </div>

      {(!findings.data || findings.data.length === 0) ? (
        <div className="pt-12 text-ink/40 font-serif text-lg tracking-tight">
          No semantic matches found.
        </div>
      ) : (
        <ul className="flex flex-col gap-1 pb-24">
          <AnimatePresence initial={false}>
            {findings.data.map((finding) => {
              const isActive = activeFindingId === finding.id;

              return (
                <SearchFindingItem
                  key={finding.id}
                  finding={finding}
                  isActive={isActive}
                  isCondensed={hasActiveFinding}
                  onClick={() => {
                    if (isActive) {
                      dispatch({ type: "SELECT_FINDING", payload: null });
                    } else {
                      dispatch({ type: "SELECT_FINDING", payload: finding.id });
                    }
                  }}
                />
              );
            })}
          </AnimatePresence>
        </ul>
      )}
    </motion.div>
  );
}
