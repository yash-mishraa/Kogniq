export type KnowledgeConceptId = string;

export interface KnowledgeConcept {
  id: KnowledgeConceptId;
  label: string;
  explanation: string;
  importance: "primary" | "secondary" | "tertiary"; // For typography-driven hierarchy
}

export interface KnowledgeRelationship {
  sourceId: KnowledgeConceptId;
  targetId: KnowledgeConceptId;
  label?: string; // Optional context, e.g., "Contains", "Enables"
}

export interface KnowledgeEvidence {
  conceptId: KnowledgeConceptId;
  documentId: string;
  snippet: string;
}

export interface KnowledgeGraph {
  concepts: KnowledgeConcept[];
  relationships: KnowledgeRelationship[];
  evidence: KnowledgeEvidence[];
}
