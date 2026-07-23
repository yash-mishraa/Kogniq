"use client";

import type { LearningMode } from "@/app/workspace/environments/study/StudyTypes";
import { motion } from "framer-motion";

interface StudyTimelineProps {
  activeMode: LearningMode;
}

const MODES: { id: LearningMode; label: string }[] = [
  { id: "understand", label: "Understand" },
  { id: "review", label: "Review" },
  { id: "recall", label: "Recall" },
  { id: "test", label: "Test" },
];

export function StudyTimeline({ activeMode }: StudyTimelineProps) {
  const activeIndex = MODES.findIndex(m => m.id === activeMode);

  return (
    <div className="flex items-center gap-4 text-xs font-mono uppercase tracking-widest">
      {MODES.map((mode, i) => {
        const isActive = mode.id === activeMode;
        const isPast = i < activeIndex;

        return (
          <div key={mode.id} className="flex items-center gap-4">
            <span
              className={`transition-colors duration-500 ${
                isActive ? "text-ink font-medium" : isPast ? "text-ink/40" : "text-ink/20"
              }`}
            >
              {mode.label}
              {isActive && (
                <motion.div
                  layoutId="study-timeline-indicator"
                  className="h-[1px] w-full bg-ink mt-1"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
            </span>
            {i < MODES.length - 1 && (
              <span className="text-ink/10">↓</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
