"use client";

import { useFlashcards } from "@/app/workspace/environments/flashcards/FlashcardsContext";
import { useEffect } from "react";

export function FlashcardsNavigator() {
  const { state, dispatch } = useFlashcards();
  const { currentIndex, cards } = state;
  const total = cards.length;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }
      if (e.key === "ArrowRight") {
        e.preventDefault();
        dispatch({ type: "NEXT_CARD" });
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        dispatch({ type: "PREV_CARD" });
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [dispatch]);

  if (total === 0) return null;

  return (
    <div className="flex items-center space-x-6">
      <button
        className="text-sm font-medium text-tertiary hover:text-primary transition-colors flex items-center space-x-1"
        onClick={() => dispatch({ type: "SHUFFLE" })}
        aria-label="Shuffle cards"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 3 21 3 21 8"></polyline><line x1="4" y1="20" x2="21" y2="3"></line><polyline points="21 16 21 21 16 21"></polyline><line x1="15" y1="15" x2="21" y2="21"></line><line x1="4" y1="4" x2="9" y2="9"></line></svg>
        <span>Shuffle</span>
      </button>

      <div className="flex items-center space-x-4">
        <button
          className={`p-2 rounded-full transition-colors ${
            currentIndex > 0
              ? "text-primary hover:bg-secondary/10"
              : "text-tertiary opacity-50 cursor-not-allowed"
          }`}
          onClick={() => dispatch({ type: "PREV_CARD" })}
          disabled={currentIndex === 0}
          aria-label="Previous card"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
        </button>

        <span className="text-sm font-medium text-secondary tabular-nums min-w-[3ch] text-center">
          {currentIndex + 1} / {total}
        </span>

        <button
          className={`p-2 rounded-full transition-colors ${
            currentIndex < total - 1
              ? "text-primary hover:bg-secondary/10"
              : "text-tertiary opacity-50 cursor-not-allowed"
          }`}
          onClick={() => dispatch({ type: "NEXT_CARD" })}
          disabled={currentIndex === total - 1}
          aria-label="Next card"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </button>
      </div>

      <button
        className="text-sm font-medium text-tertiary hover:text-primary transition-colors flex items-center space-x-1"
        onClick={() => dispatch({ type: "RESTART" })}
        aria-label="Restart deck"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"></polyline><polyline points="23 20 23 14 17 14"></polyline><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path></svg>
        <span>Restart</span>
      </button>
    </div>
  );
}
