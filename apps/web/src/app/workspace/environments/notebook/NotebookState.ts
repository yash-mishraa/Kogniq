import type { NotebookState, NotebookAction } from "./NotebookTypes";
import { abortResourceHydration, startResourceHydration } from "@/lib/core/ResourceState";

export const initialNotebookState: NotebookState = {
  notebooks: {
    status: "idle",
    data: null,
    error: null,
  },
  activeNotebookId: null,
};

export function notebookReducer(state: NotebookState, action: NotebookAction): NotebookState {
  switch (action.type) {
    case "SET_NOTEBOOKS":
      return { ...state, notebooks: action.payload };
    case "START_HYDRATION":
      return { ...state, notebooks: startResourceHydration(state.notebooks, action.payload.requestId) };
    case "ABORT_HYDRATION":
      return { ...state, notebooks: abortResourceHydration(state.notebooks, action.payload.requestId) };
    case "SET_ACTIVE_NOTEBOOK":
      return { ...state, activeNotebookId: action.payload };
    case "ADD_THOUGHT": {
      // In a real implementation this would immutably add the thought.
      // Since it's mock data, we just return state for now.
      return state;
    }
    default:
      return state;
  }
}
