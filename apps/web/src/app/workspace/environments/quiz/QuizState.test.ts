import { describe, expect, it } from "vitest";
import { initialQuizState, isQuestionCorrect, quizReducer, quizScore } from "./QuizState";
import type { QuizQuestionData } from "@/lib/services/interfaces/IQuizService";

const questions: readonly QuizQuestionData[] = [
  { id: "one", question: "One?", options: [{ id: "A", text: "Alpha" }, { id: "B", text: "Beta" }, { id: "C", text: "Gamma" }, { id: "D", text: "Delta" }], correctOptionId: "B", explanation: "Beta is correct.", difficulty: "easy", tags: [] },
  { id: "two", question: "Two?", options: [{ id: "A", text: "Alpha" }, { id: "B", text: "Beta" }, { id: "C", text: "Gamma" }, { id: "D", text: "Delta" }], correctOptionId: "C", explanation: "Gamma is correct.", difficulty: "medium", tags: [] },
];

function loaded() {
  let state = quizReducer(initialQuizState, { type: "LOAD_STARTED", payload: { documentId: "doc", requestId: "request" } });
  state = quizReducer(state, { type: "LOAD_SUCCEEDED", payload: { documentId: "doc", requestId: "request", questions } });
  return state;
}

describe("quizReducer", () => {
  it("starts idle and loads questions only for the current request", () => {
    expect(initialQuizState.status).toBe("idle");
    const state = loaded();
    expect(state.status).toBe("ready");
    expect(state.questions).toEqual(questions);
    expect(quizReducer(state, { type: "LOAD_EMPTY", payload: { documentId: "other", requestId: "old" } })).toBe(state);
  });

  it("handles empty and failed loads", () => {
    const loading = quizReducer(initialQuizState, { type: "LOAD_STARTED", payload: { documentId: "doc", requestId: "request" } });
    expect(quizReducer(loading, { type: "LOAD_EMPTY", payload: { documentId: "doc", requestId: "request" } }).status).toBe("empty");
    expect(quizReducer(loading, { type: "LOAD_FAILED", payload: { documentId: "doc", requestId: "request", error: new Error("offline") } }).error?.message).toBe("offline");
  });

  it("replaces an unsubmitted selection, locks it after submission, and derives a score once", () => {
    let state = loaded();
    state = quizReducer(state, { type: "SELECT_OPTION", payload: { questionId: "one", optionId: "A" } });
    state = quizReducer(state, { type: "SELECT_OPTION", payload: { questionId: "one", optionId: "B" } });
    expect(state.selectedOptionIds.one).toBe("B");
    state = quizReducer(state, { type: "SUBMIT_CURRENT" });
    expect(isQuestionCorrect(state, "one")).toBe(true);
    expect(quizScore(state)).toBe(1);
    const submitted = quizReducer(state, { type: "SUBMIT_CURRENT" });
    expect(quizScore(submitted)).toBe(1);
    expect(quizReducer(submitted, { type: "SELECT_OPTION", payload: { questionId: "one", optionId: "A" } })).toEqual(submitted);
  });

  it("supports incorrect answers, navigation, completion, review, restart, and reset", () => {
    let state = loaded();
    state = quizReducer(state, { type: "SELECT_OPTION", payload: { questionId: "one", optionId: "A" } });
    state = quizReducer(state, { type: "SUBMIT_CURRENT" });
    expect(quizScore(state)).toBe(0);
    state = quizReducer(state, { type: "NEXT" });
    expect(state.currentIndex).toBe(1);
    expect(quizReducer(state, { type: "NEXT" })).toBe(state);
    state = quizReducer(state, { type: "SELECT_OPTION", payload: { questionId: "two", optionId: "C" } });
    state = quizReducer(state, { type: "SUBMIT_CURRENT" });
    state = quizReducer(state, { type: "NEXT" });
    expect(state.status).toBe("completed");
    state = quizReducer(state, { type: "REVIEW", payload: { index: 0 } });
    expect(state.currentIndex).toBe(0);
    state = quizReducer(state, { type: "RESTART" });
    expect(state.selectedOptionIds).toEqual({});
    expect(state.submittedQuestionIds).toEqual({});
    expect(quizReducer(state, { type: "RESET" })).toEqual(initialQuizState);
  });
});
