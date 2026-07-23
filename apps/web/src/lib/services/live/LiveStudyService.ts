import type { IStudyService, GenerateStudyParams } from "../interfaces/IStudyService";
import type { StudyMaterial } from "@/app/workspace/environments/study/StudyTypes";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { REQUEST_POLICIES } from "@/lib/api/policies";

export class LiveStudyService implements IStudyService {
  async generateMaterial(params: GenerateStudyParams): Promise<StudyMaterial> {
    const response = await apiClient.post<StudyMaterial>(
      ENDPOINTS.learning.generate,
      { topicId: params.topicId },
      {
        signal: params.signal,
        ...REQUEST_POLICIES.retrieval
      }
    );
    return response.data;
  }
}
