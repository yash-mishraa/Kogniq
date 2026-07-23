"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import type { SearchState, SearchAction } from "./SearchTypes";
import { initialSearchState, searchReducer } from "./SearchState";

interface SearchContextValue {
  state: SearchState;
  dispatch: React.Dispatch<SearchAction>;
}

const SearchContext = createContext<SearchContextValue | null>(null);

export function SearchProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(searchReducer, initialSearchState);

  return (
    <SearchContext.Provider value={{ state, dispatch }}>
      {children}
    </SearchContext.Provider>
  );
}

export function useSearch() {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error("useSearch must be used within a SearchProvider");
  }
  return context;
}
