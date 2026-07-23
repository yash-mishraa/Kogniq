"use client";

import { useEffect } from "react";
import { useSearch, SearchProvider } from "./SearchContext";
import { SearchSurface, SearchEmptyState, SearchFindings, SearchThinkingState } from "@/components/search";
import { MOCK_FINDINGS } from "./SearchState";

function SearchEnvironmentBody() {
  const { state, dispatch } = useSearch();

  useEffect(() => {
    if (state.retrievalState === "idle" && state.query) {
      dispatch({ type: "SET_RETRIEVAL_STATE", payload: "connecting" });
      
      // Simulate "connecting related concepts" state
      const timer1 = setTimeout(() => {
        dispatch({ type: "SET_RETRIEVAL_STATE", payload: "found" });
        
        // Mock retrieval logic:
        const queryLower = state.query.toLowerCase();
        let found = false;
        
        for (const [key, results] of Object.entries(MOCK_FINDINGS)) {
          if (queryLower.includes(key) || key.includes(queryLower)) {
            dispatch({ type: "SET_FINDINGS", payload: results });
            found = true;
            break;
          }
        }
        
        if (!found) {
          // If no mock match, just return empty or default to the first one for demonstration
          dispatch({ type: "SET_FINDINGS", payload: [] });
          // If we wanted an empty state, we could set retrievalState to "empty"
          // dispatch({ type: "SET_RETRIEVAL_STATE", payload: "empty" });
        }
        
      }, 1500);

      return () => clearTimeout(timer1);
    }
  }, [state.query, state.retrievalState, dispatch]);

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
