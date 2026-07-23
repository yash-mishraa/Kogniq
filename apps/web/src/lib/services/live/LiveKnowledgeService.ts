import type { IKnowledgeService } from "../interfaces/IKnowledgeService";
import type { KnowledgeGraph } from "@/app/workspace/environments/knowledge/KnowledgeTypes";
import { apiClient } from "@/lib/api/client";
import { REQUEST_POLICIES } from "@/lib/api/policies";

export class LiveKnowledgeService implements IKnowledgeService {
  async getKnowledgeMap(signal?: AbortSignal): Promise<KnowledgeGraph> {
    const response = await apiClient.get<KnowledgeGraph>("/api/v1/knowledge", {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }
}
