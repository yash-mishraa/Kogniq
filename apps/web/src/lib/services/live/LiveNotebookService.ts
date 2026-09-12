import type { INotebookService } from "../interfaces/INotebookService";
import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";
import { apiClient } from "@/lib/api/client";

interface LearningMaterials {
  studyGuide?: { body: string };
}

export class LiveNotebookService implements INotebookService {
  async getNotebooks(signal?: AbortSignal, documentId?: string): Promise<Notebook[]> {
    if (!documentId) return [];

    while (true) {
      if (signal?.aborted) {
        throw new Error("Aborted");
      }

      const response = await apiClient.get<{ status: string; materials: LearningMaterials | null }>(
        `/api/v1/learning/${documentId}`,
        { signal }
      );

      const data = response.data;
      if (data.status === "failed" || data.status === "error") {
        throw new Error("Failed to generate learning material");
      }
      if (data.status === "completed" || data.status === "COMPLETED_WITH_WARNINGS" || (data.status === "COMPLETED" && data.materials)) {
        if (!data.materials) {
           throw new Error("Materials were empty but status was completed");
        }

        const studyGuide = data.materials.studyGuide?.body || "";
        if (!studyGuide) return [];

        const notebook: Notebook = {
          id: documentId,
          title: "Study Guide Notebook",
          history: [
            { timestamp: "Just now", description: "Generated from source document" }
          ],
          entries: [
            {
              id: "entry-1",
              title: "Generated Study Guide",
              createdAt: "Just now",
              thoughts: [
                {
                  id: "t1",
                  type: "observation",
                  content: studyGuide
                }
              ]
            }
          ]
        };

        return [notebook];
      }

      await new Promise((resolve) => setTimeout(resolve, 3000));
    }
  }
}
