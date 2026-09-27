import type { IStudentService, KnowledgeState, LearnerRecommendation } from "../interfaces/IStudentService";

export class MockStudentService implements IStudentService {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async listKnowledgeStates(signal?: AbortSignal): Promise<{ states: KnowledgeState[] }> {
    return { states: [] };
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
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

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async getRecommendations(limit: number = 5, signal?: AbortSignal): Promise<{ recommendations: LearnerRecommendation[] }> {
    return {
      recommendations: [
        {
          resource_id: "doc-1",
          resource_title: "Introduction to Kogniq",
          action_type: "new_resource",
          priority_score: 10,
          reason: "Start learning this new resource."
        }
      ]
    };
  }
}
