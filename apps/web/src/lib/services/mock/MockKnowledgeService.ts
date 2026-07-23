import type { IKnowledgeService } from "../interfaces/IKnowledgeService";
import type { KnowledgeGraph } from "@/app/workspace/environments/knowledge/KnowledgeTypes";
import { MOCK_TRANSFORMER_GRAPH } from "@/app/workspace/environments/knowledge/KnowledgeState";

export class MockKnowledgeService implements IKnowledgeService {
  async getKnowledgeMap(signal?: AbortSignal): Promise<KnowledgeGraph> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        resolve(MOCK_TRANSFORMER_GRAPH);
      }, 700);

      if (signal) {
        signal.addEventListener("abort", () => {
          clearTimeout(timeout);
          reject(new DOMException("Aborted", "AbortError"));
        });
      }
    });
  }
}
