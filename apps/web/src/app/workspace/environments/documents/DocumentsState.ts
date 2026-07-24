import type { DocumentsState, DocumentsAction, DocumentItem } from "./DocumentsTypes";
import { abortResourceHydration, startResourceHydration } from "@/lib/core/ResourceState";

export const MOCK_DOCUMENTS: DocumentItem[] = [];

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
    case "START_HYDRATION":
      return {
        ...state,
        documents: startResourceHydration(state.documents, action.payload.requestId),
      };
    case "ABORT_HYDRATION":
      return {
        ...state,
        documents: abortResourceHydration(state.documents, action.payload.requestId),
      };
    default:
      return state;
  }
}
