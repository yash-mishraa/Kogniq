import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "@/lib/api/client";
import { LiveQuizService, mapPersistedQuiz } from "./LiveQuizService";

const validQuiz = [{ id: "q1", question: "Question?", options: [{ id: "A", text: "One" }, { id: "B", text: "Two" }, { id: "C", text: "Three" }, { id: "D", text: "Four" }], correct_answer: " two ", explanation: "Because two.", difficulty: "easy", tags: ["topic"] }];

describe("LiveQuizService", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("maps the persisted four-option contract and resolves the correct option by text", () => {
    expect(mapPersistedQuiz(validQuiz)[0]).toMatchObject({ correctOptionId: "B", difficulty: "easy" });
    expect(mapPersistedQuiz([])).toEqual([]);
  });

  it("returns an empty collection when no quiz is persisted", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValue({ data: { status: "completed", materials: {} }, status: 200 });
    await expect(new LiveQuizService().getQuiz({ documentId: "doc" })).resolves.toEqual([]);
  });

  it("returns an empty collection when learning content is unavailable", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValue({ data: { status: "failed", materials: null }, status: 200 });
    await expect(new LiveQuizService().getQuiz({ documentId: "doc" })).resolves.toEqual([]);
  });

  it("rejects malformed quiz data and unmatched correct answers instead of guessing", () => {
    expect(() => mapPersistedQuiz([{ ...validQuiz[0], options: validQuiz[0].options.slice(0, 3) }])).toThrow("four options");
    expect(() => mapPersistedQuiz([{ ...validQuiz[0], correct_answer: "Missing" }])).toThrow("unmatched correct answer");
  });

  it("surfaces API failures and respects aborts", async () => {
    vi.spyOn(apiClient, "get").mockRejectedValue(new Error("network down"));
    await expect(new LiveQuizService().getQuiz({ documentId: "doc" })).rejects.toThrow("network down");
    const controller = new AbortController();
    controller.abort();
    await expect(new LiveQuizService().getQuiz({ documentId: "doc", signal: controller.signal })).rejects.toMatchObject({ name: "AbortError" });
  });
});
