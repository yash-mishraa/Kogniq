import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { REQUEST_POLICIES } from "@/lib/api/policies";
import type { IStudentService, KnowledgeState } from "../interfaces/IStudentService";

export class LiveStudentService implements IStudentService {
  async listKnowledgeStates(signal?: AbortSignal): Promise<{ states: KnowledgeState[] }> {
    const response = await apiClient.get<{ states: KnowledgeState[] }>(
      ENDPOINTS.student.knowledgeStates,
      {
        signal,
        ...REQUEST_POLICIES.retrieval
      }
    );
    return response.data;
  }

  async getKnowledgeState(resourceId: string, signal?: AbortSignal): Promise<KnowledgeState> {
    const response = await apiClient.get<KnowledgeState>(
      ENDPOINTS.student.knowledgeState(resourceId),
      {
        signal,
        ...REQUEST_POLICIES.retrieval
      }
    );
    return response.data;
  }

  async getRecommendations(limit: number = 5, signal?: AbortSignal): Promise<{ recommendations: any[] }> {
    const response = await apiClient.get<{ recommendations: any[] }>(
      ENDPOINTS.student.recommendations,
      {
        params: { limit },
        signal,
        ...REQUEST_POLICIES.retrieval
      }
    );
    return response.data;
  }
}
