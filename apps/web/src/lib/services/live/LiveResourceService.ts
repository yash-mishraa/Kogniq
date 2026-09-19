import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { REQUEST_POLICIES } from "@/lib/api/policies";
import type { 
  IResourceService, 
  LearningResource, 
  ResourceSection, 
  ResourceChunk, 
  ResourceStatistics 
} from "../interfaces/IResourceService";

export class LiveResourceService implements IResourceService {
  async listResources(limit = 50, offset = 0, signal?: AbortSignal): Promise<LearningResource[]> {
    const response = await apiClient.get<LearningResource[]>(ENDPOINTS.resources.list, {
      params: { limit, offset },
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }

  async getResource(resourceId: string, signal?: AbortSignal): Promise<LearningResource> {
    const response = await apiClient.get<LearningResource>(ENDPOINTS.resources.get(resourceId), {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }

  async getResourceSections(resourceId: string, signal?: AbortSignal): Promise<ResourceSection[]> {
    const response = await apiClient.get<ResourceSection[]>(ENDPOINTS.resources.sections(resourceId), {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }

  async getResourceChunks(resourceId: string, limit = 100, offset = 0, signal?: AbortSignal): Promise<ResourceChunk[]> {
    const response = await apiClient.get<ResourceChunk[]>(ENDPOINTS.resources.chunks(resourceId), {
      params: { limit, offset },
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }

  async getResourceStatistics(resourceId: string, signal?: AbortSignal): Promise<ResourceStatistics> {
    const response = await apiClient.get<ResourceStatistics>(ENDPOINTS.resources.statistics(resourceId), {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }
}
