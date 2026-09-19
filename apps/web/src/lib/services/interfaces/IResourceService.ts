export interface ResourceSection {
  id: string;
  resource_id: string;
  title: string;
  order: number;
  page_start: number | null;
  page_end: number | null;
  char_start: number | null;
  char_end: number | null;
}

export interface ResourceChunk {
  id: string;
  resource_id: string;
  section_id: string | null;
  text: string | null;
  order: number;
  checksum: string | null;
  token_estimate: number | null;
  metadata: Record<string, unknown>;
}

export interface LearningResource {
  id: string;
  title: string;
  resource_type: string;
  source: string;
  checksum: string | null;
  language: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ResourceStatistics {
  section_count: number;
  chunk_count: number;
  total_tokens: number;
}

export interface IResourceService {
  listResources(limit?: number, offset?: number, signal?: AbortSignal): Promise<LearningResource[]>;
  getResource(resourceId: string, signal?: AbortSignal): Promise<LearningResource>;
  getResourceSections(resourceId: string, signal?: AbortSignal): Promise<ResourceSection[]>;
  getResourceChunks(resourceId: string, limit?: number, offset?: number, signal?: AbortSignal): Promise<ResourceChunk[]>;
  getResourceStatistics(resourceId: string, signal?: AbortSignal): Promise<ResourceStatistics>;
}
