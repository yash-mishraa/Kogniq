import type { StudioGraphState } from "./StudioTypes";

export interface StudioState {
  graph: StudioGraphState;
  isPreview: boolean;
}

export type StudioAction =
  | { type: "SET_GRAPH"; payload: StudioGraphState }
  | { type: "START_HYDRATION"; payload: { requestId: string } }
  | { type: "ABORT_HYDRATION"; payload: { requestId: string } }
  | { type: "SET_PREVIEW"; payload: boolean }
  | { type: "TOGGLE_PREVIEW" };
