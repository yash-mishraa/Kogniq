"use client";

import { useSearch } from "@/app/workspace/environments/search/SearchContext";
import { Locus } from "@/components/locus";
import { SearchFilters } from "./SearchFilters";

export function SearchEmptyState() {
  const { dispatch, state } = useSearch();

  const handleQuery = (query: string) => {
    dispatch({ type: "SET_QUERY", payload: query });
  };

  return (
    <section aria-label="Search starting point" className="flex flex-col flex-1 items-start pt-4 gap-8">
      <div className="w-full max-w-3xl">
        <Locus 
          environmentTitle="Search" 
          placeholder="Search your knowledge..."
          mode="free-text"
          onSubmitQuery={handleQuery}
          autoFocus 
        />
      </div>
      <SearchFilters activeFilter={state.activeFilter} onFilterChange={(f) => dispatch({ type: "SET_FILTER", payload: f })} />
    </section>
  );
}
