export interface QuizOptionData {
  id: "A" | "B" | "C" | "D";
  text: string;
}

export interface QuizQuestionData {
  id: string;
  question: string;
  options: readonly QuizOptionData[];
  correctOptionId: QuizOptionData["id"];
  explanation: string;
  difficulty: "easy" | "medium" | "hard";
  tags: readonly string[];
}

export interface GetQuizParams {
  documentId: string;
  signal?: AbortSignal;
}

export interface IQuizService {
  getQuiz(params: GetQuizParams): Promise<readonly QuizQuestionData[]>;
}
