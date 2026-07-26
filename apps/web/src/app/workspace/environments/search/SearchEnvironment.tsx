"use client";

import { useEffect } from "react";
import { useSearch, SearchProvider } from "./SearchContext";
import { SearchSurface, SearchFindings, SearchThinkingState } from "@/components/search";
import { serviceProvider } from "@/lib/providers";

import { Locus } from "@/components/locus";
import { SearchFilters } from "@/components/search/SearchFilters";

function SearchEnvironmentBody() {
  const { state, dispatch } = useSearch();

  const handleQuery = (query: string) => {
    dispatch({ type: "SET_QUERY", payload: query });
  };

  useEffect(() => {
    if (state.query) {
      let isMounted = true;
      const currentRequestId = crypto.randomUUID();
      dispatch({ type: "SET_RETRIEVAL_STATE", payload: "connecting" });
      dispatch({ type: "START_HYDRATION", payload: { requestId: currentRequestId } });
      
      const controller = new AbortController();
      
      async function retrieve() {
        try {
          const data = await serviceProvider.getProvider().search.search({
            query: state.query,
            filter: state.activeFilter,
            signal: controller.signal
          });
          
          if (isMounted) {
            dispatch({ type: "SET_FINDINGS", payload: { status: "ready", data, error: null, requestId: currentRequestId } });
            dispatch({ type: "SET_RETRIEVAL_STATE", payload: data.length > 0 ? "found" : "empty" });
          }
        } catch (err: unknown) {
          if (isMounted) {
            if (err instanceof Error && err.name === "AbortError") return;
            dispatch({ type: "SET_FINDINGS", payload: { status: "error", data: null, error: err as Error, requestId: currentRequestId } });
            dispatch({ type: "SET_RETRIEVAL_STATE", payload: "empty" }); // Or a new error state if preferred
          }
        }
      }

      retrieve();
      return () => {
        isMounted = false;
        controller.abort();
      };
    }
    
  }, [state.query, state.activeFilter, dispatch]);

  return (
    <SearchSurface>
      <div className="flex flex-col flex-shrink-0 w-full mb-12 gap-6">
        <Locus 
          environmentTitle="Search" 
          placeholder="Search your knowledge..."
          mode="free-text"
          onSubmitQuery={handleQuery}
          autoFocus={true} 
        />
        <SearchFilters activeFilter={state.activeFilter} onFilterChange={(f) => dispatch({ type: "SET_FILTER", payload: f })} />
      </div>

      {state.retrievalState === "idle" && !state.query && (
         <div className="pt-12 text-ink/40 font-serif text-lg tracking-tight">
           Enter a query above to search your knowledge base.
         </div>
      )}
      {state.retrievalState === "connecting" && <SearchThinkingState />}
      {(state.retrievalState === "found" || state.retrievalState === "empty") && <SearchFindings />}
    </SearchSurface>
  );
}

export function SearchEnvironment() {
  return (
    <SearchProvider>
      <SearchEnvironmentBody />
    </SearchProvider>
  );
}
