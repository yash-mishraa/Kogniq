export type DocumentStatus = "imported" | "processing" | "chunking" | "embedding" | "knowledge-extraction" | "ready";

export interface DocumentItem {
  id: string;
  title: string;
  source: string; // e.g., 'Transformer Architecture.pdf'
  importDate: string;
  status: DocumentStatus;
  pageCount?: number;
  readingTime?: number; // in minutes
  chunkCount?: number;
  extractedConcepts?: number;
  content?: string; // Mock content for reading
}

export interface DocumentsState {
  documents: DocumentItem[];
  activeDocumentId: string | null;
}

export type DocumentsAction =
  | { type: "IMPORT_DOCUMENT"; payload: DocumentItem }
  | { type: "SELECT_DOCUMENT"; payload: string | null }
  | { type: "UPDATE_STATUS"; payload: { id: string; status: DocumentStatus } };
