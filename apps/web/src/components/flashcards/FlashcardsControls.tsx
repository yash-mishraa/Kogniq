"use client";

import { useFlashcards } from "@/app/workspace/environments/flashcards/FlashcardsContext";
import type { LearnerResponse } from "@/app/workspace/environments/flashcards/FlashcardsTypes";

export function FlashcardsControls() {
  const { state, dispatch } = useFlashcards();
  const { cards, order, currentIndex, isFlipped } = state;
  const currentCard = cards[order[currentIndex]];

  if (!isFlipped || !currentCard) return null;

  const handleResponse = (response: LearnerResponse) => {
    dispatch({ type: "RECORD_RESPONSE", payload: { cardId: currentCard.id, response } });
    setTimeout(() => {
      dispatch({ type: "NEXT_CARD" });
    }, 150);
  };

  return (
    <div className="flex space-x-4 items-center justify-center mt-8">
      <button
        onClick={() => handleResponse("again")}
        className="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 font-medium rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
      >
        Again
      </button>
      <button
        onClick={() => handleResponse("hard")}
        className="px-4 py-2 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 font-medium rounded-lg hover:bg-orange-200 dark:hover:bg-orange-900/50 transition-colors"
      >
        Hard
      </button>
      <button
        onClick={() => handleResponse("good")}
        className="px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
      >
        Good
      </button>
      <button
        onClick={() => handleResponse("easy")}
        className="px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 font-medium rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
      >
        Easy
      </button>
    </div>
  );
}
