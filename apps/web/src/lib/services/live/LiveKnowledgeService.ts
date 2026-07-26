import type { IKnowledgeService } from "../interfaces/IKnowledgeService";
import type { KnowledgeGraph } from "@/app/workspace/environments/knowledge/KnowledgeTypes";
import { apiClient } from "@/lib/api/client";
import { REQUEST_POLICIES } from "@/lib/api/policies";

export class LiveKnowledgeService implements IKnowledgeService {
  async getKnowledgeMap(documentId: string, signal?: AbortSignal): Promise<KnowledgeGraph> {
    if (!documentId) {
      return { concepts: [], relationships: [], evidence: [] };
    }

    try {
      const response = await apiClient.get<KnowledgeGraph>(`/api/v1/knowledge/${documentId}`, {
        signal,
        ...REQUEST_POLICIES.retrieval
      });
      
      const data = response.data || {};
      return {
        concepts: data.concepts || [],
        relationships: data.relationships || [],
        evidence: data.evidence || []
      };
    } catch {
      // Return empty graph instead of crashing on structured failure
      return { concepts: [], relationships: [], evidence: [] };
    }
  }
}
