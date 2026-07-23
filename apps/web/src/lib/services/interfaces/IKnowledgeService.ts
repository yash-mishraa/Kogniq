import type { KnowledgeGraph } from "@/app/workspace/environments/knowledge/KnowledgeTypes";

export interface IKnowledgeService {
  getKnowledgeMap(signal?: AbortSignal): Promise<KnowledgeGraph>;
}
