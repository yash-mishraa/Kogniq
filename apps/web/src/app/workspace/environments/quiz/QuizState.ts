import type { QuizState, QuizAction } from "./QuizTypes";

export const initialQuizState: QuizState = {
  status: "idle",
  documentId: null,
  requestId: null,
  questions: [],
  currentIndex: 0,
  selectedOptionIds: {},
  submittedQuestionIds: {},
  error: null,
};

function isCurrentRequest(state: QuizState, documentId: string, requestId: string): boolean {
  return state.documentId === documentId && state.requestId === requestId;
}

export function quizReducer(state: QuizState, action: QuizAction): QuizState {
  switch (action.type) {
    case "LOAD_STARTED":
      return { ...initialQuizState, status: "loading", documentId: action.payload.documentId, requestId: action.payload.requestId };
    case "LOAD_SUCCEEDED":
      if (!isCurrentRequest(state, action.payload.documentId, action.payload.requestId)) return state;
      return { ...state, status: "ready", questions: action.payload.questions, currentIndex: 0, error: null };
    case "LOAD_EMPTY":
      if (!isCurrentRequest(state, action.payload.documentId, action.payload.requestId)) return state;
      return { ...state, status: "empty", questions: [], error: null };
    case "LOAD_FAILED":
      if (!isCurrentRequest(state, action.payload.documentId, action.payload.requestId)) return state;
      return { ...state, status: "error", questions: [], error: action.payload.error };
    case "SELECT_OPTION":
      if (state.submittedQuestionIds[action.payload.questionId]) return state;
      return { ...state, selectedOptionIds: { ...state.selectedOptionIds, [action.payload.questionId]: action.payload.optionId } };
    case "SUBMIT_CURRENT": {
      const currentQuestion = state.questions[state.currentIndex];
      if (!currentQuestion || state.submittedQuestionIds[currentQuestion.id] || !state.selectedOptionIds[currentQuestion.id]) return state;
      return { ...state, submittedQuestionIds: { ...state.submittedQuestionIds, [currentQuestion.id]: true } };
    }
    case "NEXT":
      if (!state.submittedQuestionIds[state.questions[state.currentIndex]?.id]) return state;
      if (state.currentIndex === state.questions.length - 1) return { ...state, status: "completed" };
      return { ...state, currentIndex: state.currentIndex + 1 };
    case "PREVIOUS":
      if (state.currentIndex === 0) return state;
      return { ...state, status: state.status === "completed" ? "ready" : state.status, currentIndex: state.currentIndex - 1 };
    case "REVIEW":
      if (action.payload.index < 0 || action.payload.index >= state.questions.length) return state;
      return { ...state, status: "ready", currentIndex: action.payload.index };
    case "RESTART":
      if (!state.questions.length) return state;
      return { ...state, status: "ready", currentIndex: 0, selectedOptionIds: {}, submittedQuestionIds: {}, error: null };
    case "RESET":
      return initialQuizState;
  }
}

export function isQuestionCorrect(state: QuizState, questionId: string): boolean {
  const question = state.questions.find((item) => item.id === questionId);
  return Boolean(question && state.selectedOptionIds[questionId] === question.correctOptionId);
}

export function quizScore(state: QuizState): number {
  return state.questions.filter((question) => state.submittedQuestionIds[question.id] && isQuestionCorrect(state, question.id)).length;
}
