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

export interface DocumentBlock {
  id: string;
  text: string;
  type: string;
  bbox?: [number, number, number, number] | null;
  order: number;
}

export interface DocumentPage {
  page_number: number;
  width?: number | null;
  height?: number | null;
  blocks: DocumentBlock[];
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
  content?: string; // Optional raw string for backward compatibility
  pages?: DocumentPage[]; // Structured extraction data
  semantics?: SemanticDocument | null;
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
  | { type: "DELETE_DOCUMENT"; payload: string }
  | { type: "UPDATE_DOCUMENT"; payload: Partial<DocumentItem> & { id: string } }
  | { type: "START_HYDRATION"; payload: { requestId: string } }
  | { type: "ABORT_HYDRATION"; payload: { requestId: string } };
export interface SemanticBoundingBox {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

export interface SemanticSection {
  id: string;
  page_number: number;
  title: string;
  level: number;
  parent_id?: string | null;
  bbox?: SemanticBoundingBox | null;
}

export interface SemanticFigure {
  id: string;
  page_number: number;
  figure_number?: string | null;
  caption?: string | null;
  bbox?: SemanticBoundingBox | null;
  image_bbox?: SemanticBoundingBox | null;
}

export interface SemanticDocument {
  document_id: string;
  status: "ready" | "unavailable";
  semantic_version?: string | null;
  sections: SemanticSection[];
  figures: SemanticFigure[];
}
