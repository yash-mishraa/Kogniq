import type { GetQuizParams, IQuizService, QuizQuestionData } from "../interfaces/IQuizService";

/** Mock mode deliberately has no educational fallback content. */
export class MockQuizService implements IQuizService {
  async getQuiz({ signal }: GetQuizParams): Promise<readonly QuizQuestionData[]> {
    if (signal?.aborted) throw new DOMException("The quiz request was aborted.", "AbortError");
    return [];
  }
}
