"use client";

import type { RecallContent } from "@/app/workspace/environments/study/StudyTypes";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface StudyRecallProps {
  content: RecallContent;
}

export function StudyRecall({ content }: StudyRecallProps) {
  const [isRevealed, setIsRevealed] = useState(false);

  useEffect(() => {
    setIsRevealed(false);
  }, [content.prompt]);

  return (
    <div className="flex flex-col gap-12 max-w-2xl" id={content.prompt}>
      <h2 className="text-2xl font-serif leading-snug text-ink tracking-tight">
        {content.prompt}
      </h2>

      <AnimatePresence mode="wait">
        {!isRevealed ? (
          <motion.div
            key="hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <button
              onClick={() => setIsRevealed(true)}
              className="text-sm font-mono uppercase tracking-widest text-ink/40 hover:text-ink transition-colors outline-none"
            >
              Reveal Explanation ↓
            </button>
          </motion.div>
        ) : (
          <motion.div
            key="revealed"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-6"
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
