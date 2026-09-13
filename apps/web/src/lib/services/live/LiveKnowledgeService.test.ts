import { describe, it, expect, vi, beforeEach } from "vitest";
import { LiveKnowledgeService } from "./LiveKnowledgeService";
import { apiClient } from "@/lib/api/client";

vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe("LiveKnowledgeService", () => {
  let service: LiveKnowledgeService;

  beforeEach(() => {
    service = new LiveKnowledgeService();
    vi.resetAllMocks();
  });

  it("should return empty graph if documentId is empty", async () => {
    const result = await service.getKnowledgeMap("");
    expect(result.concepts).toHaveLength(0);
    expect(result.relationships).toHaveLength(0);
    expect(apiClient.get).not.toHaveBeenCalled();
  });

  it("should correctly map backend response to frontend types", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      status: 200,
      headers: new Headers(),
      data: {
        concepts: [
          {
            id: "c1",
            name: "Neural Networks",
            description: "A type of machine learning model",
            concept_type: "THEORY",
          },
          {
            id: "c2",
            name: "Backpropagation",
            description: "Algorithm for training",
            concept_type: "ALGORITHM",
          },
          {
            id: "c3",
            name: "Cat",
            description: "An animal",
            concept_type: "EXAMPLE",
          },
        ],
        relationships: [
          {
            source_concept: "c1",
            target_concept: "c2",
            relationship_type: "USES",
          },
        ],
      },
    } as unknown as { status: number; headers: Headers; data: unknown });

    const result = await service.getKnowledgeMap("doc-123");

    expect(result.concepts).toHaveLength(3);
    
    // Check mapping
    expect(result.concepts[0]).toEqual({
      id: "c1",
      label: "Neural Networks",
      explanation: "A type of machine learning model",
      importance: "primary", // mapped from THEORY
    });

    expect(result.concepts[1].importance).toBe("primary"); // mapped from ALGORITHM
    expect(result.concepts[2].importance).toBe("tertiary"); // mapped from EXAMPLE

    expect(result.relationships).toHaveLength(1);
    expect(result.relationships[0]).toEqual({
      sourceId: "c1",
      targetId: "c2",
      label: "USES",
    });
  });

  it("should handle malformed backend responses gracefully", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      status: 200,
      headers: new Headers(),
      data: {
        concepts: [
          { name: "Missing ID" }, // No ID, should be filtered out
          { id: "c2" }, // Missing name, should fallback
        ],
        relationships: [
          { source_concept: "c1" }, // Missing target
          { target_concept: "c2" }, // Missing source
        ],
      },
    } as unknown as { status: number; headers: Headers; data: unknown });

    const result = await service.getKnowledgeMap("doc-123");

    expect(result.concepts).toHaveLength(1);
    expect(result.concepts[0].id).toBe("c2");
    expect(result.concepts[0].label).toBe("Unknown Concept");
    expect(result.concepts[0].explanation).toBe("");
    expect(result.concepts[0].importance).toBe("secondary"); // Fallback importance

    // Relationships without both source and target should be filtered out
    expect(result.relationships).toHaveLength(0);
  });

  it("should return empty graph on API failure", async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("Network Error"));

    const result = await service.getKnowledgeMap("doc-123");

    expect(result.concepts).toHaveLength(0);
    expect(result.relationships).toHaveLength(0);
  });

  it("should rethrow AbortError", async () => {
    const abortError = new DOMException("Aborted", "AbortError");
    vi.mocked(apiClient.get).mockRejectedValueOnce(abortError);

    await expect(service.getKnowledgeMap("doc-123")).rejects.toThrow("Aborted");
  });
});
