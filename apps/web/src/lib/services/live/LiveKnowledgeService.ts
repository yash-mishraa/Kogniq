import type { IKnowledgeService } from "../interfaces/IKnowledgeService";
import type { 
  KnowledgeGraph, 
  KnowledgeConcept, 
  KnowledgeRelationship 
} from "@/app/workspace/environments/knowledge/KnowledgeTypes";
import { apiClient } from "@/lib/api/client";
import { REQUEST_POLICIES } from "@/lib/api/policies";

interface ApiKnowledgeConcept {
  id?: string;
  name?: string;
  description?: string;
  concept_type?: string | number;
}

interface ApiKnowledgeRelationship {
  source_concept?: string;
  target_concept?: string;
  relationship_type?: string | number;
}

interface ApiKnowledgeGraph {
  concepts?: ApiKnowledgeConcept[];
  relationships?: ApiKnowledgeRelationship[];
}

function mapImportance(type?: string | number): "primary" | "secondary" | "tertiary" {
  if (!type) return "secondary";
  const strType = typeof type === "number" ? mapConceptTypeEnum(type) : String(type).toUpperCase();
  if (["THEORY", "PRINCIPLE", "ALGORITHM", "DATA_STRUCTURE"].includes(strType)) return "primary";
  if (["EXAMPLE", "EXERCISE", "UNKNOWN"].includes(strType)) return "tertiary";
  return "secondary";
}

function mapConceptTypeEnum(val: number): string {
  // Map python Enum auto() values to strings
  const map: Record<number, string> = {
    1: "DEFINITION", 2: "ALGORITHM", 3: "FORMULA", 4: "DATA_STRUCTURE", 
    5: "THEORY", 6: "EXAMPLE", 7: "EXERCISE", 8: "FACT", 9: "PRINCIPLE", 10: "UNKNOWN"
  };
  return map[val] || "UNKNOWN";
}

function mapRelationshipTypeEnum(val: number): string {
  const map: Record<number, string> = {
    1: "DEPENDS_ON", 2: "USES", 3: "DEFINES", 4: "REFERENCES",
    5: "EXTENDS", 6: "IMPLEMENTS", 7: "EXPLAINS", 8: "RELATED_TO"
  };
  return map[val] || "RELATED_TO";
}

export class LiveKnowledgeService implements IKnowledgeService {
  async getKnowledgeMap(documentId: string, signal?: AbortSignal): Promise<KnowledgeGraph> {
    if (!documentId) {
      return { concepts: [], relationships: [], evidence: [] };
    }

    try {
      const response = await apiClient.get<ApiKnowledgeGraph>(`/api/v1/knowledge/${documentId}`, {
        signal,
        ...REQUEST_POLICIES.retrieval
      });
      
      const data = response.data || {};
      const apiConcepts = Array.isArray(data.concepts) ? data.concepts : [];
      const apiRelationships = Array.isArray(data.relationships) ? data.relationships : [];

      const concepts: KnowledgeConcept[] = apiConcepts.map(c => ({
        id: c.id || "",
        label: c.name || "Unknown Concept",
        explanation: c.description || "",
        importance: mapImportance(c.concept_type),
      })).filter(c => c.id !== "");

      const relationships: KnowledgeRelationship[] = apiRelationships.map(r => ({
        sourceId: r.source_concept || "",
        targetId: r.target_concept || "",
        label: typeof r.relationship_type === "number" ? mapRelationshipTypeEnum(r.relationship_type) : String(r.relationship_type || ""),
      })).filter(r => r.sourceId !== "" && r.targetId !== "");

      return {
        concepts,
        relationships,
        evidence: [] // Backend currently doesn't provide snippet evidence at graph level
      };
    } catch (err: unknown) {
      if (err && typeof err === "object" && "name" in err && err.name === "AbortError") {
        throw err;
      }
      return { concepts: [], relationships: [], evidence: [] };
    }
  }
}
