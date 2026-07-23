export type ThoughtType = "observation" | "question" | "reflection" | "connection" | "reminder";

export interface NotebookAnnotation {
  id: string;
  content: string;
  type: "highlight" | "marginalia";
}

export interface KnowledgeReference {
  id: string;
  sourceType: "document" | "concept" | "search" | "study" | "note";
  title: string;
  path: string[];
}

export interface NotebookThought {
  id: string;
  type: ThoughtType;
  content: string;
  annotations?: NotebookAnnotation[];
  references?: KnowledgeReference[];
}

export interface NotebookEntry {
  id: string;
  title: string;
  createdAt: string;
  thoughts: NotebookThought[];
}

export interface NotebookHistory {
  description: string;
  timestamp: string;
}

export interface Notebook {
  id: string;
  title: string;
  history: NotebookHistory[];
  entries: NotebookEntry[];
}

export interface NotebookState {
  notebooks: Notebook[];
  activeNotebookId: string | null;
}

export type NotebookAction =
  | { type: "SET_ACTIVE_NOTEBOOK"; payload: string }
  | { type: "ADD_THOUGHT"; payload: { notebookId: string; entryId: string; thought: NotebookThought } };
