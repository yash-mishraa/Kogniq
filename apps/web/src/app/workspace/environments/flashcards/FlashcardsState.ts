import type { FlashcardsState, FlashcardsAction } from "./FlashcardsTypes";

export const initialFlashcardsState: FlashcardsState = {
  status: "idle",
  error: null,
  cards: [],
  order: [],
  currentIndex: 0,
  isFlipped: false,
  completedCount: 0,
  responses: {},
};

function generateSequentialOrder(length: number): number[] {
  return Array.from({ length }, (_, i) => i);
}

function generateShuffledOrder(length: number): number[] {
  const order = generateSequentialOrder(length);
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return order;
}

export function flashcardsReducer(state: FlashcardsState, action: FlashcardsAction): FlashcardsState {
  switch (action.type) {
    case "START_LOAD":
      return {
        ...state,
        status: "loading",
        error: null,
        requestId: action.payload.requestId,
      };

    case "LOAD_SUCCESS":
      if (state.requestId && state.requestId !== action.payload.requestId) return state;
      return {
        ...state,
        status: "ready",
        error: null,
        cards: action.payload.cards,
        order: generateSequentialOrder(action.payload.cards.length),
        currentIndex: 0,
        isFlipped: false,
        completedCount: 0,
        responses: {},
      };

    case "LOAD_ERROR":
      if (state.requestId && state.requestId !== action.payload.requestId) return state;
      return {
        ...state,
        status: "error",
        error: action.payload.error,
        cards: [],
        order: [],
      };

    case "LOAD_EMPTY":
      if (state.requestId && state.requestId !== action.payload.requestId) return state;
      return {
        ...state,
        status: "empty",
        error: null,
        cards: [],
        order: [],
      };

    case "FLIP_CARD":
      return {
        ...state,
        isFlipped: !state.isFlipped,
      };

    case "NEXT_CARD":
      if (state.currentIndex < state.cards.length - 1) {
        return {
          ...state,
          currentIndex: state.currentIndex + 1,
          isFlipped: false,
        };
      }
      return state;

    case "PREV_CARD":
      if (state.currentIndex > 0) {
        return {
          ...state,
          currentIndex: state.currentIndex - 1,
          isFlipped: false,
        };
      }
      return state;

    case "SHUFFLE":
      return {
        ...state,
        order: generateShuffledOrder(state.cards.length),
        currentIndex: 0,
        isFlipped: false,
      };

    case "RESTART":
      return {
        ...state,
        order: generateSequentialOrder(state.cards.length),
        currentIndex: 0,
        isFlipped: false,
        completedCount: 0,
        responses: {},
      };

    case "RECORD_RESPONSE": {
      const isNewCompletion = !state.responses[action.payload.cardId];
      return {
        ...state,
        responses: {
          ...state.responses,
          [action.payload.cardId]: action.payload.response,
        },
        completedCount: isNewCompletion ? state.completedCount + 1 : state.completedCount,
      };
    }

    case "RESET_ENVIRONMENT":
      return initialFlashcardsState;

    default:
      return state;
  }
}
