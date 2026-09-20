import type { IStudentService, KnowledgeState } from "../interfaces/IStudentService";

export class MockStudentService implements IStudentService {
  async listKnowledgeStates(signal?: AbortSignal): Promise<{ states: KnowledgeState[] }> {
    return { states: [] };
  }

  async getKnowledgeState(resourceId: string, signal?: AbortSignal): Promise<KnowledgeState> {
    return {
      id: "mock-1",
      user_id: "user-1",
      resource_id: resourceId,
      mastery_score: 0.85,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_reviewed_at: new Date().toISOString(),
      next_review_due: new Date().toISOString()
    };
  }
}
