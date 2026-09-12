"use client";

import { motion } from "framer-motion";
import type { FlashcardData } from "@/lib/services/interfaces/IFlashcardsService";
import { useEffect } from "react";
import ReactMarkdown from "react-markdown";

interface FlashcardItemProps {
  card: FlashcardData;
  isFlipped: boolean;
  onFlip: () => void;
}

export function FlashcardItem({ card, isFlipped, onFlip }: FlashcardItemProps) {
  // Use space/enter to flip
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Avoid triggering on inputs or textareas
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        onFlip();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onFlip]);

  return (
    <div
      className="relative w-full max-w-2xl aspect-[3/2] cursor-pointer"
      style={{ perspective: "1000px" }}
      onClick={onFlip}
      role="button"
      tabIndex={0}
      aria-pressed={isFlipped}
      aria-label={isFlipped ? "Show question" : "Show answer"}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onFlip();
        }
      }}
    >
      <motion.div
        className="w-full h-full relative"
        style={{ transformStyle: "preserve-3d" }}
        animate={{ rotateX: isFlipped ? 180 : 0 }}
        transition={{ duration: 0.4, type: "spring", stiffness: 260, damping: 20 }}
      >
        {/* Front */}
        <div
          className="absolute inset-0 flex flex-col justify-center items-center p-8 lg:p-12 text-center bg-surface border border-secondary rounded-2xl shadow-sm overflow-y-auto"
          style={{ backfaceVisibility: "hidden" }}
        >
          <span className="text-xs font-medium text-tertiary uppercase tracking-wider mb-4">Question</span>
          <div className="prose prose-sm md:prose-base dark:prose-invert">
            <ReactMarkdown>{card.question}</ReactMarkdown>
          </div>
        </div>

        {/* Back */}
        <div
          className="absolute inset-0 flex flex-col justify-center items-center p-8 lg:p-12 text-center bg-surface-alt border border-primary rounded-2xl shadow-md overflow-y-auto"
          style={{ backfaceVisibility: "hidden", transform: "rotateX(180deg)" }}
        >
          <span className="text-xs font-medium text-primary uppercase tracking-wider mb-4">Answer</span>
          <div className="prose prose-sm md:prose-base dark:prose-invert">
            <ReactMarkdown>{card.answer}</ReactMarkdown>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
