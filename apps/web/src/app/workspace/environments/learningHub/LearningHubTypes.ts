import type { LearningResource, ResourceSection, ResourceChunk, ResourceStatistics } from "@/lib/services/interfaces/IResourceService";
import type { ResourceProgress } from "@/lib/services/interfaces/IAnalyticsService";

export interface LearningHubState {
  resources: {
    status: "idle" | "loading" | "ready" | "error";
    data: LearningResource[] | null;
    error: Error | null;
    limit: number;
    offset: number;
    hasMore: boolean;
  };
  activeResourceId: string | null;
  activeResourceDetails: {
    status: "idle" | "loading" | "ready" | "error";
    sections: ResourceSection[];
    chunks: ResourceChunk[];
    chunkLimit: number;
    chunkOffset: number;
    hasMoreChunks: boolean;
    isLoadingMoreChunks: boolean;
    statistics: ResourceStatistics | null;
    progress: ResourceProgress | null;
    error: Error | null;
  };
}

export type LearningHubAction =
  | { type: "LOAD_RESOURCES_START" }
  | { type: "LOAD_RESOURCES_SUCCESS"; payload: { data: LearningResource[]; hasMore: boolean; offset: number } }
  | { type: "LOAD_RESOURCES_ERROR"; payload: Error }
  | { type: "SELECT_RESOURCE"; payload: string | null }
  | { type: "LOAD_RESOURCE_DETAILS_START" }
  | { type: "LOAD_RESOURCE_DETAILS_SUCCESS"; payload: { sections: ResourceSection[]; chunks: ResourceChunk[]; statistics: ResourceStatistics; progress: ResourceProgress | null; hasMoreChunks: boolean; chunkOffset: number } }
  | { type: "LOAD_RESOURCE_DETAILS_ERROR"; payload: Error }
  | { type: "LOAD_MORE_CHUNKS_START" }
  | { type: "LOAD_MORE_CHUNKS_SUCCESS"; payload: { chunks: ResourceChunk[]; hasMoreChunks: boolean; chunkOffset: number } }
  | { type: "LOAD_MORE_CHUNKS_ERROR"; payload: Error }
  | { type: "UPDATE_PROGRESS"; payload: ResourceProgress };
