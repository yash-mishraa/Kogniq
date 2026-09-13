"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import type { StudioState, StudioAction } from "./StudioState";
import { abortResourceHydration, startResourceHydration } from "@/lib/core/ResourceState";

export const initialState: StudioState = {
  graph: {
    status: "idle",
    data: null,
    error: null,
    requestId: undefined,
  },
  isPreview: false,
};

export function studioReducer(state: StudioState, action: StudioAction): StudioState {
  switch (action.type) {
    case "SET_GRAPH":
      if (state.graph.requestId && action.payload.requestId !== state.graph.requestId) {
        return state;
      }
      return { ...state, graph: action.payload };
    case "START_HYDRATION":
      return { ...state, graph: startResourceHydration(state.graph, action.payload.requestId) };
    case "ABORT_HYDRATION":
      return { ...state, graph: abortResourceHydration(state.graph, action.payload.requestId) };
    case "SET_PREVIEW":
      return { ...state, isPreview: action.payload };
    case "TOGGLE_PREVIEW":
      return { ...state, isPreview: !state.isPreview };
    default:
      return state;
  }
}

const StudioContext = createContext<{
  state: StudioState;
  dispatch: React.Dispatch<StudioAction>;
} | null>(null);

export function StudioProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(studioReducer, initialState);
  return <StudioContext.Provider value={{ state, dispatch }}>{children}</StudioContext.Provider>;
}

export function useStudio() {
  const context = useContext(StudioContext);
  if (!context) throw new Error("useStudio must be used within StudioProvider");
  return context;
}
