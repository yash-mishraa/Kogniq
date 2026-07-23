"use client";

import type { NotebookThought as ThoughtType } from "@/app/workspace/environments/notebook/NotebookTypes";
import { NotebookAnnotation } from "./NotebookAnnotation";
import { NotebookConnection } from "./NotebookConnection";

interface NotebookThoughtProps {
  thought: ThoughtType;
}

export function NotebookThought({ thought }: NotebookThoughtProps) {
  // Determine styling based on the type of thought
  let textStyle = "text-xl font-serif leading-relaxed text-ink/90";
  let label = "";

  if (thought.type === "question") {
    textStyle = "text-2xl font-serif leading-snug text-ink tracking-tight italic";
    label = "Question";
  } else if (thought.type === "reflection") {
    textStyle = "text-xl font-serif leading-relaxed text-ink/80 border-l-2 border-ink/10 pl-6";
    label = "Reflection";
  } else if (thought.type === "reminder") {
    textStyle = "text-lg font-mono text-ink/70 leading-relaxed";
    label = "Reminder";
  } else if (thought.type === "connection") {
    textStyle = "text-xl font-serif leading-relaxed text-ink/80 italic";
    label = "Connection";
  }

  return (
    <div className="flex flex-col gap-4 relative group w-full">
      
      {/* The main thought content */}
      <div className="w-full max-w-2xl">
        {label && (
          <div className="text-[10px] uppercase tracking-widest font-medium text-ink/30 mb-2 transition-opacity duration-300 opacity-0 group-hover:opacity-100">
            {label}
          </div>
        )}
        <p className={textStyle}>
          {thought.content}
        </p>
      </div>

      {/* Marginalia and References mapped to the right margin area */}
      <div className="md:absolute md:left-full md:top-0 md:pl-16 w-48 flex flex-col gap-6 mt-4 md:mt-0">
        {thought.annotations?.map(annotation => (
          <NotebookAnnotation key={annotation.id} annotation={annotation} />
        ))}
        {thought.references?.map(reference => (
          <NotebookConnection key={reference.id} reference={reference} />
        ))}
      </div>
      
    </div>
  );
}
