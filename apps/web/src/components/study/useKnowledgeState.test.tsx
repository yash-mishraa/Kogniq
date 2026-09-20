import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { useKnowledgeState } from "./useKnowledgeState";
import { serviceProvider } from "@/lib/providers";

describe("useKnowledgeState", () => {
  beforeEach(() => {
    serviceProvider.setMode("mock");
    vi.clearAllMocks();
  });

  it("should return null immediately if resourceId is null", () => {
    const { result } = renderHook(() => useKnowledgeState(null));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.knowledgeState).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("should fetch and return knowledge state successfully", async () => {
    const mockState = {
      id: "state-1",
      user_id: "u-1",
      resource_id: "doc-1",
      mastery_score: 0.75,
      created_at: "2026-09-20T00:00:00Z",
      updated_at: "2026-09-20T00:00:00Z",
      last_reviewed_at: null,
      next_review_due: null,
    };

    const spy = vi
      .spyOn(serviceProvider.getProvider().student, "getKnowledgeState")
      .mockResolvedValueOnce(mockState);

    const { result } = renderHook(() => useKnowledgeState("doc-1"));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.knowledgeState).toEqual(mockState);
    expect(result.current.error).toBeNull();
    expect(spy).toHaveBeenCalledWith("doc-1", expect.any(AbortSignal));
  });

  it("should return null and no error for 404", async () => {
    const error404 = new Error("Not Found") as any;
    error404.status = 404;

    const spy = vi
      .spyOn(serviceProvider.getProvider().student, "getKnowledgeState")
      .mockRejectedValueOnce(error404);

    const { result } = renderHook(() => useKnowledgeState("doc-2"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.knowledgeState).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("should return error for 500", async () => {
    const error500 = new Error("Server Error") as any;
    error500.status = 500;

    const spy = vi
      .spyOn(serviceProvider.getProvider().student, "getKnowledgeState")
      .mockRejectedValueOnce(error500);

    const { result } = renderHook(() => useKnowledgeState("doc-3"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.knowledgeState).toBeNull();
    expect(result.current.error).toEqual(error500);
  });
});
