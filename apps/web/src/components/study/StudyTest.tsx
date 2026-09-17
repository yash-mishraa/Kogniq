"use client";

import type { TestContent } from "@/app/workspace/environments/study/StudyTypes";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";

interface StudyTestProps {
  content: TestContent;
}

export function StudyTest({ content }: StudyTestProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);
  const { memory } = useWorkspace();
  const documentId = memory.documents?.openedDocument;

  useEffect(() => {
    setSelectedIndex(null);
    setAiExplanation(null);
    setIsExplaining(false);
  }, [content.question]);

  const handleExplain = async () => {
    if (!documentId || selectedIndex === null) return;
    setIsExplaining(true);
    try {
      const res = await fetch("/api/v1/learning/explain-mistake", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_id: documentId,
          question_id: content.id,
          selected_option_id: content.options[selectedIndex].id
        })
      });
      if (res.ok) {
        const data = await res.json();
        setAiExplanation(data.explanation);
      }
    } catch (e) {
      console.error("Failed to explain mistake", e);
    } finally {
      setIsExplaining(false);
    }
  };

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
              {option.text}
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
            {selectedIndex !== content.correctOptionIndex && !aiExplanation && (
              <button 
                onClick={handleExplain}
                disabled={isExplaining}
                className="self-start text-sm px-4 py-2 bg-ink/5 hover:bg-ink/10 text-ink rounded flex items-center gap-2"
              >
                {isExplaining ? "AI is typing..." : "Explain my mistake"}
              </button>
            )}
            {aiExplanation && (
              <div className="bg-ink/5 p-4 rounded-lg border-l-2 border-ink/20">
                <p className="text-sm font-sans text-ink/90 leading-relaxed">
                  <strong>AI Tutor:</strong> {aiExplanation}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
