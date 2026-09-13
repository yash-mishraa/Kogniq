import type { ResourceState } from "@/lib/core/ResourceState";

export interface StudioGraphConcept {
  id: string;
  name: string;
  description: string;
}

export interface StudioGraphData {
  concepts: StudioGraphConcept[];
}

export type StudioGraphState = ResourceState<StudioGraphData, Error>;
