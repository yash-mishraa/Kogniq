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

export interface IStudentService {
  listKnowledgeStates(signal?: AbortSignal): Promise<{ states: KnowledgeState[] }>;
  getKnowledgeState(resourceId: string, signal?: AbortSignal): Promise<KnowledgeState>;
}
