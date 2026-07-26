import type { KnowledgeGraph } from "@/app/workspace/environments/knowledge/KnowledgeTypes";

export interface IKnowledgeService {
  getKnowledgeMap(documentId: string, signal?: AbortSignal): Promise<KnowledgeGraph>;
}
