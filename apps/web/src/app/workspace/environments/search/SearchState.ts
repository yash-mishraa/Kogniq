import type { SearchState, SearchAction, SearchFinding } from "./SearchTypes";

export const MOCK_FINDINGS: Record<string, SearchFinding[]> = {
  "self attention": [
    {
      id: "finding-1",
      title: "Transformer Architecture",
      documentId: "doc-1",
      relevanceExplanation: "Directly explains the mechanism of self-attention where tokens attend to other tokens in the same sequence.",
      evidence: {
        snippet: "...every token attends to every other token in the sequence, allowing the model to dynamically weigh context...",
        location: "Section 3, Paragraph 2",
      },
      relatedConcepts: ["Attention Weights", "Multi-Head Attention", "Query-Key-Value"],
    },
    {
      id: "finding-2",
      title: "Deep Learning Research",
      documentId: "doc-4",
      relevanceExplanation: "Discusses the evolution of sequence models toward self-attention mechanisms.",
      evidence: {
        snippet: "...dispensing with recurrence and convolutions entirely in favor of attention mechanisms...",
        location: "Abstract",
      },
      relatedConcepts: ["Recurrent Neural Networks", "Transformers"],
    }
  ],
  "database": [
    {
      id: "finding-3",
      title: "Database Normalization",
      documentId: "doc-2",
      relevanceExplanation: "Covers the fundamental principles of database structure and normalization forms.",
      evidence: {
        snippet: "...the process of structuring a relational database to reduce data redundancy and improve data integrity...",
        location: "Chapter 4, Section 1",
      },
      relatedConcepts: ["1NF", "2NF", "3NF", "BCNF", "Data Integrity"],
    }
  ]
};

export const initialSearchState: SearchState = {
  query: "",
  activeFilter: "all",
  retrievalState: "idle",
  findings: [],
  activeFindingId: null,
};

export function searchReducer(state: SearchState, action: SearchAction): SearchState {
  switch (action.type) {
    case "SET_QUERY":
      return { ...state, query: action.payload, activeFindingId: null };
    case "SET_FILTER":
      return { ...state, activeFilter: action.payload };
    case "SET_RETRIEVAL_STATE":
      return { ...state, retrievalState: action.payload };
    case "SET_FINDINGS":
      return { ...state, findings: action.payload };
    case "SELECT_FINDING":
      return { ...state, activeFindingId: action.payload };
    case "RESET":
      return initialSearchState;
    default:
      return state;
  }
}
