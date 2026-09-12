export interface FlashcardData {
  id: string;
  question: string;
  answer: string;
  difficulty?: string;
}

export interface GetFlashcardsParams {
  documentId: string;
  signal?: AbortSignal;
}

export interface IFlashcardsService {
  getFlashcards(params: GetFlashcardsParams): Promise<FlashcardData[]>;
}
