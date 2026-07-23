import type { DocumentItem } from "@/app/workspace/environments/documents/DocumentsTypes";

export interface ProcessDocumentParams {
  file: File;
  signal?: AbortSignal;
}

export interface IDocumentService {
  processDocument(params: ProcessDocumentParams): Promise<DocumentItem>;
  getDocuments(signal?: AbortSignal): Promise<DocumentItem[]>;
}
