"use client";

import { createContext, useContext, useReducer, ReactNode, Dispatch } from "react";
import { AnalyticsState, AnalyticsAction } from "./AnalyticsTypes";
import { initialAnalyticsState, analyticsReducer } from "./AnalyticsState";

const AnalyticsContext = createContext<{ state: AnalyticsState; dispatch: Dispatch<AnalyticsAction> } | null>(null);

export function AnalyticsProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(analyticsReducer, initialAnalyticsState);
  return (
    <AnalyticsContext.Provider value={{ state, dispatch }}>
      {children}
    </AnalyticsContext.Provider>
  );
}

export function useAnalytics() {
  const value = useContext(AnalyticsContext);
  if (!value) throw new Error("useAnalytics must be used within AnalyticsProvider");
  return value;
}
