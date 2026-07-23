export type SearchFilter = "all" | "documents" | "concepts" | "learning";

export type RetrievalState = "idle" | "connecting" | "found" | "empty";

export interface SearchEvidence {
  snippet: string;
  location: string;
}

export interface SearchFinding {
  id: string;
  title: string;
  documentId: string;
  relevanceExplanation: string;
  evidence: SearchEvidence;
  relatedConcepts: string[];
}

import type { ResourceState } from "@/lib/core/ResourceState";

export interface SearchState {
  query: string;
  activeFilter: SearchFilter;
  retrievalState: RetrievalState;
  findings: ResourceState<SearchFinding[]>;
  activeFindingId: string | null;
}

export type SearchAction =
  | { type: "SET_QUERY"; payload: string }
  | { type: "SET_FILTER"; payload: SearchFilter }
  | { type: "SET_RETRIEVAL_STATE"; payload: RetrievalState }
  | { type: "SET_FINDINGS"; payload: ResourceState<SearchFinding[]> }
  | { type: "SELECT_FINDING"; payload: string | null }
  | { type: "RESET" };
