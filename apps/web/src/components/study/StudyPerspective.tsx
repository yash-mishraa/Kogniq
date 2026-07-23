"use client";

import type { StudyState } from "@/app/workspace/environments/study/StudyTypes";
import { motion, AnimatePresence } from "framer-motion";
import { StudyUnderstand } from "./StudyUnderstand";
import { StudyReview } from "./StudyReview";
import { StudyRecall } from "./StudyRecall";
import { StudyTest } from "./StudyTest";

interface StudyPerspectiveProps {
  state: StudyState;
}

export function StudyPerspective({ state }: StudyPerspectiveProps) {
  if (!state.material) return null;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={state.activeMode}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="w-full h-full"
      >
        {state.activeMode === "understand" && <StudyUnderstand content={state.material.understand} />}
        {state.activeMode === "review" && <StudyReview content={state.material.review} />}
        {state.activeMode === "recall" && <StudyRecall content={state.material.recall[state.recallIndex]} />}
        {state.activeMode === "test" && <StudyTest content={state.material.test[state.testIndex]} />}
      </motion.div>
    </AnimatePresence>
  );
}
