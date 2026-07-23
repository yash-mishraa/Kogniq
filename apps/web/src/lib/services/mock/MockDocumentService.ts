import type { IDocumentService, ProcessDocumentParams } from "../interfaces/IDocumentService";
import type { DocumentItem } from "@/app/workspace/environments/documents/DocumentsTypes";
import { MOCK_DOCUMENTS } from "@/app/workspace/environments/documents/DocumentsState";

export class MockDocumentService implements IDocumentService {
  async getDocuments(signal?: AbortSignal): Promise<DocumentItem[]> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        resolve(MOCK_DOCUMENTS);
      }, 500);

      if (signal) {
        signal.addEventListener("abort", () => {
          clearTimeout(timeout);
          reject(new DOMException("Aborted", "AbortError"));
        });
      }
    });
  }

  async processDocument(params: ProcessDocumentParams): Promise<DocumentItem> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        const newItem: DocumentItem = {
          id: `doc-${Date.now()}`,
          title: params.file.name,
          source: params.file.name,
          status: "ready",
          importDate: new Date().toISOString()
        };
        resolve(newItem);
      }, 2000);

      if (params.signal) {
        params.signal.addEventListener("abort", () => {
          clearTimeout(timeout);
          reject(new DOMException("Aborted", "AbortError"));
        });
      }
    });
  }
}
