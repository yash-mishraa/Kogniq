export type DocumentStatus = "Uploaded" | "Extracting" | "Normalizing" | "Chunking" | "Persisted" | "Ready" | "Failed";

export interface DocumentProcessingResult {
  document_id: string;
  filename: string;
  processor: string;
  chunk_count: number;
  processing_time_ms: number;
  status: DocumentStatus;
  warnings: string[];
}

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
