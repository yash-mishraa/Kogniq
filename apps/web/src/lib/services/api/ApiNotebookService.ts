import type { INotebookService } from "../interfaces/INotebookService";
import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";
import { apiClient } from "@/lib/api/client";

export class ApiNotebookService implements INotebookService {
  async getNotebooks(signal?: AbortSignal, documentId?: string): Promise<Notebook[]> {
    if (!documentId) {
      return [];
    }
    const response = await apiClient.get<{ notebooks: Notebook[] }>(
      `/notebooks?document_id=${documentId}`,
      { signal }
    );
    return response.data.notebooks;
  }

  async appendNote(
    documentId: string, 
    title: string, 
    content: string, 
    idempotencyKey?: string
  ): Promise<{ status: string; entry_id?: string }> {
    const response = await apiClient.post<{ status: string; entry_id?: string }>(
      `/notebooks/${documentId}/entries`,
      {
        title,
        content,
        idempotency_key: idempotencyKey,
      }
    );
    return response.data;
  }
}
