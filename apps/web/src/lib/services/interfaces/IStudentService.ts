export interface KnowledgeState {
  id: string;
  user_id: string;
  resource_id: string;
  mastery_score: number;
  created_at: string;
  updated_at: string;
  last_reviewed_at: string | null;
  next_review_due: string | null;
}

export interface LearnerRecommendation {
  resource_id: string;
  resource_title: string;
  action_type: string;
  priority_score: number;
  reason: string;
}

export interface IStudentService {
  listKnowledgeStates(signal?: AbortSignal): Promise<{ states: KnowledgeState[] }>;
  getKnowledgeState(resourceId: string, signal?: AbortSignal): Promise<KnowledgeState>;
  getRecommendations(limit?: number, signal?: AbortSignal): Promise<{ recommendations: LearnerRecommendation[] }>;
}
