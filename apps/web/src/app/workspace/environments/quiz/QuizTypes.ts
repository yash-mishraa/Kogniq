import type { QuizQuestionData } from "@/lib/services/interfaces/IQuizService";

export type QuizStatus = "idle" | "loading" | "ready" | "completed" | "empty" | "error";

export interface QuizState {
  status: QuizStatus;
  documentId: string | null;
  requestId: string | null;
  questions: readonly QuizQuestionData[];
  currentIndex: number;
  selectedOptionIds: Readonly<Record<string, string | undefined>>;
  submittedQuestionIds: Readonly<Record<string, true | undefined>>;
  error: Error | null;
}

export type QuizAction =
  | { type: "LOAD_STARTED"; payload: { documentId: string; requestId: string } }
  | { type: "LOAD_SUCCEEDED"; payload: { documentId: string; requestId: string; questions: readonly QuizQuestionData[] } }
  | { type: "LOAD_EMPTY"; payload: { documentId: string; requestId: string } }
  | { type: "LOAD_FAILED"; payload: { documentId: string; requestId: string; error: Error } }
  | { type: "SELECT_OPTION"; payload: { questionId: string; optionId: string } }
  | { type: "SUBMIT_CURRENT" }
  | { type: "NEXT" }
  | { type: "PREVIOUS" }
  | { type: "REVIEW"; payload: { index: number } }
  | { type: "RESTART" }
  | { type: "RESET" };
