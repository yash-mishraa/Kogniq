"use client";

import type { TestContent } from "@/app/workspace/environments/study/StudyTypes";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface StudyTestProps {
  content: TestContent;
}

export function StudyTest({ content }: StudyTestProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  useEffect(() => {
    setSelectedIndex(null);
  }, [content.question]);

  return (
    <div className="flex flex-col gap-12 max-w-3xl" id={content.question}>
      <h2 className="text-2xl font-serif leading-snug text-ink tracking-tight">
        {content.question}
      </h2>

      <div className="flex flex-col gap-4">
        {content.options.map((option, index) => {
          const isSelected = selectedIndex === index;
          const isCorrect = index === content.correctOptionIndex;
          const showResult = selectedIndex !== null;

          let buttonClass = "text-left px-6 py-4 rounded-lg font-serif text-lg leading-relaxed transition-all duration-300 outline-none ";

          if (!showResult) {
            buttonClass += "bg-ink/[0.02] hover:bg-ink/[0.04] text-ink/80";
          } else {
            if (isCorrect) {
              buttonClass += "bg-emerald-500/10 text-emerald-900 border-l-4 border-emerald-500";
            } else if (isSelected) {
              buttonClass += "bg-rose-500/10 text-rose-900 border-l-4 border-rose-500 opacity-60";
            } else {
              buttonClass += "bg-transparent text-ink/30 opacity-40";
            }
          }

          return (
            <button
              key={index}
              onClick={() => {
                if (selectedIndex === null) setSelectedIndex(index);
              }}
              disabled={showResult}
              className={buttonClass}
            >
              {option}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        {selectedIndex !== null && (
          <motion.div
            key="explanation"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-6 pt-4"
          >
            <div className="h-[1px] w-12 bg-ink/10" />
            <p className="text-xl font-serif leading-relaxed text-ink/80">
              {content.explanation}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
