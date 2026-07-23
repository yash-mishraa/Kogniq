import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";

export interface INotebookService {
  getNotebooks(signal?: AbortSignal): Promise<Notebook[]>;
}
