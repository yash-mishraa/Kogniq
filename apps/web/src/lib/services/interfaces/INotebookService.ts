import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";

export interface INotebookService {
  getNotebooks(signal?: AbortSignal, documentId?: string): Promise<Notebook[]>;
  appendNote(documentId: string, title: string, content: string, idempotencyKey?: string): Promise<{ status: string; entry_id?: string }>;
}
