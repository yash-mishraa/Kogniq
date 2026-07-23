"use client";

import { useEffect } from "react";
import { useSearch, SearchProvider } from "./SearchContext";
import { SearchSurface, SearchEmptyState, SearchFindings, SearchThinkingState } from "@/components/search";
import { serviceProvider } from "@/lib/providers";

function SearchEnvironmentBody() {
  const { state, dispatch } = useSearch();

  useEffect(() => {
    if (state.retrievalState === "idle" && state.query) {
      dispatch({ type: "SET_RETRIEVAL_STATE", payload: "connecting" });
      dispatch({ type: "SET_FINDINGS", payload: { ...state.findings, status: "loading" } });
      
      const controller = new AbortController();
      
      async function retrieve() {
        try {
          const data = await serviceProvider.getProvider().search.search({
            query: state.query,
            filter: state.activeFilter,
            signal: controller.signal
          });
          
          dispatch({ type: "SET_FINDINGS", payload: { status: "ready", data, error: null } });
          dispatch({ type: "SET_RETRIEVAL_STATE", payload: data.length > 0 ? "found" : "empty" });
        } catch (err: unknown) {
          if (err instanceof Error && err.name === "AbortError") return;
          dispatch({ type: "SET_FINDINGS", payload: { status: "error", data: null, error: err as Error } });
          dispatch({ type: "SET_RETRIEVAL_STATE", payload: "empty" }); // Or a new error state if preferred
        }
      }

      retrieve();
      return () => controller.abort();
    }
  }, [state.query, state.activeFilter, state.retrievalState, dispatch, state.findings]);

  return (
    <SearchSurface>
      {state.retrievalState === "idle" && !state.query && <SearchEmptyState />}
      {state.retrievalState === "connecting" && <SearchThinkingState />}
      {state.retrievalState === "found" && <SearchFindings />}
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
