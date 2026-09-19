import type { LearningHubState, LearningHubAction } from "./LearningHubTypes";

export const initialLearningHubState: LearningHubState = {
  resources: {
    status: "idle",
    data: null,
    error: null,
    limit: 50,
    offset: 0,
    hasMore: true,
  },
  activeResourceId: null,
  activeResourceDetails: {
    status: "idle",
    sections: [],
    chunks: [],
    chunkLimit: 100,
    chunkOffset: 0,
    hasMoreChunks: true,
    isLoadingMoreChunks: false,
    statistics: null,
    progress: null,
    error: null,
  },
};

export function learningHubReducer(state: LearningHubState, action: LearningHubAction): LearningHubState {
  switch (action.type) {
    case "LOAD_RESOURCES_START":
      return {
        ...state,
        resources: { ...state.resources, status: "loading", error: null },
      };
    case "LOAD_RESOURCES_SUCCESS":
      return {
        ...state,
        resources: {
          ...state.resources,
          status: "ready",
          data: action.payload.offset === 0 
            ? action.payload.data 
            : [...(state.resources.data || []), ...action.payload.data],
          hasMore: action.payload.hasMore,
          offset: action.payload.offset,
        },
      };
    case "LOAD_RESOURCES_ERROR":
      return {
        ...state,
        resources: { ...state.resources, status: "error", error: action.payload },
      };
    case "SELECT_RESOURCE":
      return {
        ...state,
        activeResourceId: action.payload,
        activeResourceDetails: initialLearningHubState.activeResourceDetails, // reset details on selection change
      };
    case "LOAD_RESOURCE_DETAILS_START":
      return {
        ...state,
        activeResourceDetails: { ...state.activeResourceDetails, status: "loading", error: null },
      };
    case "LOAD_RESOURCE_DETAILS_SUCCESS":
      return {
        ...state,
        activeResourceDetails: {
          ...state.activeResourceDetails,
          status: "ready",
          sections: action.payload.sections,
          chunks: action.payload.chunks,
          statistics: action.payload.statistics,
          progress: action.payload.progress,
          hasMoreChunks: action.payload.hasMoreChunks,
          chunkOffset: action.payload.chunkOffset,
          isLoadingMoreChunks: false,
          error: null,
        },
      };
    case "LOAD_RESOURCE_DETAILS_ERROR":
      return {
        ...state,
        activeResourceDetails: { ...state.activeResourceDetails, status: "error", error: action.payload },
      };
    case "LOAD_MORE_CHUNKS_START":
      return {
        ...state,
        activeResourceDetails: { ...state.activeResourceDetails, isLoadingMoreChunks: true, error: null },
      };
    case "LOAD_MORE_CHUNKS_SUCCESS": {
      // Remove any duplicate chunks just in case
      const existingIds = new Set(state.activeResourceDetails.chunks.map(c => c.id));
      const newChunks = action.payload.chunks.filter(c => !existingIds.has(c.id));
      return {
        ...state,
        activeResourceDetails: {
          ...state.activeResourceDetails,
          chunks: [...state.activeResourceDetails.chunks, ...newChunks],
          hasMoreChunks: action.payload.hasMoreChunks,
          chunkOffset: action.payload.chunkOffset,
          isLoadingMoreChunks: false,
        },
      };
    }
    case "LOAD_MORE_CHUNKS_ERROR":
      return {
        ...state,
        activeResourceDetails: { ...state.activeResourceDetails, isLoadingMoreChunks: false, error: action.payload },
      };
    case "UPDATE_PROGRESS":
      return {
        ...state,
        activeResourceDetails: {
          ...state.activeResourceDetails,
          progress: action.payload,
        },
      };
    default:
      return state;
  }
}
