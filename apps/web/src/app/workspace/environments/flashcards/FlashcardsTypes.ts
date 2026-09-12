import type { FlashcardData } from "@/lib/services/interfaces/IFlashcardsService";

export type LearnerResponse = "again" | "hard" | "good" | "easy";

export interface FlashcardsState {
  status: "idle" | "loading" | "ready" | "error" | "empty";
  error: Error | null;
  requestId?: string;

  cards: FlashcardData[];
  order: number[];
  currentIndex: number;
  isFlipped: boolean;
  completedCount: number;
  
  responses: Record<string, LearnerResponse>;
}

export type FlashcardsAction =
  | { type: "START_LOAD"; payload: { requestId: string } }
  | { type: "LOAD_SUCCESS"; payload: { cards: FlashcardData[]; requestId: string } }
  | { type: "LOAD_ERROR"; payload: { error: Error; requestId: string } }
  | { type: "LOAD_EMPTY"; payload: { requestId: string } }
  | { type: "FLIP_CARD" }
  | { type: "NEXT_CARD" }
  | { type: "PREV_CARD" }
  | { type: "SHUFFLE" }
  | { type: "RESTART" }
  | { type: "RECORD_RESPONSE"; payload: { cardId: string; response: LearnerResponse } }
  | { type: "RESET_ENVIRONMENT" };
