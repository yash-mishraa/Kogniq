import type { INotebookService } from "../interfaces/INotebookService";
import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";
import { MOCK_NOTEBOOKS } from "@/app/workspace/environments/notebook/NotebookState";

export class MockNotebookService implements INotebookService {
  async getNotebooks(signal?: AbortSignal): Promise<Notebook[]> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        resolve(MOCK_NOTEBOOKS);
      }, 800);

      if (signal) {
        signal.addEventListener("abort", () => {
          clearTimeout(timeout);
          reject(new DOMException("Aborted", "AbortError"));
        });
      }
    });
  }
}
