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

import type { ResourceState } from "@/lib/core/ResourceState";

export interface DocumentsState {
  documents: ResourceState<DocumentItem[]>;
  activeDocumentId: string | null;
}

export type DocumentsAction =
  | { type: "SET_DOCUMENTS"; payload: ResourceState<DocumentItem[]> }
  | { type: "IMPORT_DOCUMENT"; payload: DocumentItem }
  | { type: "SELECT_DOCUMENT"; payload: string | null }
  | { type: "UPDATE_STATUS"; payload: { id: string; status: DocumentStatus } }
  | { type: "START_HYDRATION"; payload: { requestId: string } }
  | { type: "ABORT_HYDRATION"; payload: { requestId: string } };
