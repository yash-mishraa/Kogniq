import type { IFlashcardsService, GetFlashcardsParams, FlashcardData } from "../interfaces/IFlashcardsService";

export class MockFlashcardsService implements IFlashcardsService {
  async getFlashcards(params: GetFlashcardsParams): Promise<FlashcardData[]> {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    if (params.signal?.aborted) throw new Error("Aborted");

    return [
      {
        id: "1",
        question: "What is the capital of France?",
        answer: "Paris",
        difficulty: "easy",
      },
      {
        id: "2",
        question: "What is 2 + 2?",
        answer: "4",
        difficulty: "easy",
      },
    ];
  }
}
