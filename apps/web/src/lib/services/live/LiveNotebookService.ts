import type { INotebookService } from "../interfaces/INotebookService";
import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";
import { apiClient } from "@/lib/api/client";
import { REQUEST_POLICIES } from "@/lib/api/policies";

export class LiveNotebookService implements INotebookService {
  async getNotebooks(signal?: AbortSignal): Promise<Notebook[]> {
    const response = await apiClient.get<Notebook[]>("/api/v1/notebooks", {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }
}
