import type { 
  IResourceService, 
  LearningResource, 
  ResourceSection, 
  ResourceChunk, 
  ResourceStatistics 
} from "../interfaces/IResourceService";

/* eslint-disable @typescript-eslint/no-unused-vars */
export class MockResourceService implements IResourceService {
  async listResources(_limit = 50, _offset = 0, _signal?: AbortSignal): Promise<LearningResource[]> {
    return [];
  }

  async getResource(_resourceId: string, _signal?: AbortSignal): Promise<LearningResource> {
    throw new Error("Not implemented");
  }

  async getResourceSections(_resourceId: string, _signal?: AbortSignal): Promise<ResourceSection[]> {
    return [];
  }

  async getResourceChunks(_resourceId: string, _limit = 100, _offset = 0, _signal?: AbortSignal): Promise<ResourceChunk[]> {
    return [];
  }

  async getResourceStatistics(_resourceId: string, _signal?: AbortSignal): Promise<ResourceStatistics> {
    return { section_count: 0, chunk_count: 0, total_tokens: 0 };
  }
}
