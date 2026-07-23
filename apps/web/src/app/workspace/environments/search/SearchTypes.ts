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

export interface SearchState {
  query: string;
  activeFilter: SearchFilter;
  retrievalState: RetrievalState;
  findings: SearchFinding[];
  activeFindingId: string | null;
}

export type SearchAction =
  | { type: "SET_QUERY"; payload: string }
  | { type: "SET_FILTER"; payload: SearchFilter }
  | { type: "SET_RETRIEVAL_STATE"; payload: RetrievalState }
  | { type: "SET_FINDINGS"; payload: SearchFinding[] }
  | { type: "SELECT_FINDING"; payload: string | null }
  | { type: "RESET" };
