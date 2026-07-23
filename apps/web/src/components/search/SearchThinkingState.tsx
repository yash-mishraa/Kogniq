"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

const PHRASES = [
  "Searching your knowledge...",
  "Connecting related concepts...",
  "Found relevant passages.",
];

export function SearchThinkingState() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => Math.min(prev + 1, PHRASES.length - 1));
    }, 600); // Progress through phrases

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex flex-1 items-start justify-center pt-32">
      <div className="flex flex-col gap-3">
        {PHRASES.map((phrase, i) => {
          const isVisible = i <= index;
          const isActive = i === index;
          const isPast = i < index;

          if (!isVisible) return null;

          return (
            <motion.div
              key={phrase}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: isActive ? 1 : 0.3, y: 0 }}
              className={`font-serif text-lg tracking-tight ${
                isActive ? "text-ink" : isPast ? "text-ink/40" : "text-transparent"
              }`}
            >
              {phrase}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
