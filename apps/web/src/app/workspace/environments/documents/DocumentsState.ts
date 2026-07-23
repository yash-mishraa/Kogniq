import type { DocumentsState, DocumentsAction, DocumentItem } from "./DocumentsTypes";

export const MOCK_DOCUMENTS: DocumentItem[] = [
  {
    id: "doc-1",
    title: "Attention Is All You Need",
    source: "Transformer Architecture.pdf",
    importDate: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days ago
    status: "ready",
    pageCount: 15,
    readingTime: 45,
    chunkCount: 128,
    extractedConcepts: 42,
    content: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
  },
  {
    id: "doc-2",
    title: "Database Systems",
    source: "Database Systems Notes.md",
    importDate: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    status: "knowledge-extraction",
    pageCount: 34,
    readingTime: 120,
    chunkCount: 310,
    extractedConcepts: 15,
  },
  {
    id: "doc-3",
    title: "Linear Algebra",
    source: "Linear Algebra Handbook.pdf",
    importDate: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    status: "chunking",
    pageCount: 200,
  },
  {
    id: "doc-4",
    title: "Deep Learning Research",
    source: "Deep Learning Research Paper.pdf",
    importDate: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    status: "processing",
  },
  {
    id: "doc-5",
    title: "GATE DA Revision",
    source: "GATE DA Revision Notes.md",
    importDate: new Date(Date.now() - 1000 * 60).toISOString(),
    status: "imported",
  },
];

export const initialDocumentsState: DocumentsState = {
  documents: {
    status: "idle",
    data: null,
    error: null,
  },
  activeDocumentId: null,
};

export function documentsReducer(state: DocumentsState, action: DocumentsAction): DocumentsState {
  switch (action.type) {
    case "SET_DOCUMENTS":
      return {
        ...state,
        documents: action.payload,
      };
    case "IMPORT_DOCUMENT":
      if (!state.documents.data) return state;
      return {
        ...state,
        documents: {
          ...state.documents,
          data: [action.payload, ...state.documents.data],
        }
      };
    case "SELECT_DOCUMENT":
      return {
        ...state,
        activeDocumentId: action.payload,
      };
    case "UPDATE_STATUS":
      if (!state.documents.data) return state;
      return {
        ...state,
        documents: {
          ...state.documents,
          data: state.documents.data.map((doc) =>
            doc.id === action.payload.id ? { ...doc, status: action.payload.status } : doc
          ),
        }
      };
    default:
      return state;
  }
}
