import { ENDPOINTS } from "@/lib/api/endpoints";
import { apiClient } from "@/lib/api/client";
import type {
  GetQuizParams,
  IQuizService,
  QuizOptionData,
  QuizQuestionData,
} from "../interfaces/IQuizService";

type ApiQuizOption = { id: string; text: string };
type ApiQuizQuestion = {
  id: string;
  question: string;
  options: ApiQuizOption[];
  correct_answer: string;
  explanation: string;
  difficulty: string;
  tags: string[];
};
type LearningMaterialsResponse = {
  status: string;
  materials: { quiz?: { body: unknown } } | null;
};

const optionIds = ["A", "B", "C", "D"] as const;

function aborted(): DOMException {
  return new DOMException("The quiz request was aborted.", "AbortError");
}

function invalid(message: string): Error {
  return new Error(`Invalid persisted quiz: ${message}`);
}

function normaliseOptionText(value: string): string {
  return value.trim().toLocaleLowerCase();
}

function isDifficulty(value: string): value is QuizQuestionData["difficulty"] {
  return value === "easy" || value === "medium" || value === "hard";
}

function mapQuestion(value: unknown, index: number): QuizQuestionData {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw invalid(`question ${index + 1} is not an object.`);
  }

  const question = value as Partial<ApiQuizQuestion>;
  if (!question.id || typeof question.id !== "string") throw invalid(`question ${index + 1} has no id.`);
  if (!question.question || typeof question.question !== "string") throw invalid(`question ${index + 1} has no text.`);
  if (!question.explanation || typeof question.explanation !== "string") throw invalid(`question ${index + 1} has no explanation.`);
  if (!Array.isArray(question.options) || question.options.length !== optionIds.length) {
    throw invalid(`question ${index + 1} must have four options.`);
  }
  if (!question.correct_answer || typeof question.correct_answer !== "string") {
    throw invalid(`question ${index + 1} has no correct answer.`);
  }
  if (!question.difficulty || !isDifficulty(question.difficulty)) {
    throw invalid(`question ${index + 1} has an unsupported difficulty.`);
  }
  if (!Array.isArray(question.tags) || !question.tags.every((tag) => typeof tag === "string")) {
    throw invalid(`question ${index + 1} has invalid tags.`);
  }

  const options = question.options.map((option, optionIndex): QuizOptionData => {
    if (!option || typeof option.id !== "string" || typeof option.text !== "string") {
      throw invalid(`question ${index + 1} has an invalid option.`);
    }
    if (option.id !== optionIds[optionIndex] || !option.text.trim()) {
      throw invalid(`question ${index + 1} has invalid option labels.`);
    }
    return { id: option.id, text: option.text };
  });

  if (new Set(options.map((option) => normaliseOptionText(option.text))).size !== options.length) {
    throw invalid(`question ${index + 1} has duplicate options.`);
  }

  const correctOption = options.find(
    (option) => normaliseOptionText(option.text) === normaliseOptionText(question.correct_answer!),
  );
  if (!correctOption) throw invalid(`question ${index + 1} has an unmatched correct answer.`);

  return {
    id: question.id,
    question: question.question,
    options,
    correctOptionId: correctOption.id,
    explanation: question.explanation,
    difficulty: question.difficulty,
    tags: question.tags,
  };
}

export function mapPersistedQuiz(body: unknown): readonly QuizQuestionData[] {
  if (!Array.isArray(body)) throw invalid("quiz body is not an array.");
  return body.map(mapQuestion);
}

export class LiveQuizService implements IQuizService {
  async getQuiz({ documentId, signal }: GetQuizParams): Promise<readonly QuizQuestionData[]> {
    if (signal?.aborted) throw aborted();
    const response = await apiClient.get<LearningMaterialsResponse>(ENDPOINTS.learning.get(documentId), { signal });
    if (signal?.aborted) throw aborted();

    if (response.data.status === "failed") return [];
    if (response.data.status !== "completed") {
      throw new Error(`Unable to load quiz: unexpected learning status '${response.data.status}'.`);
    }

    const body = response.data.materials?.quiz?.body;
    return body === undefined ? [] : mapPersistedQuiz(body);
  }
}
