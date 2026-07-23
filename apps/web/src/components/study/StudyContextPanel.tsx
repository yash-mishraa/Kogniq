"use client";

import type { StudyConcept } from "@/app/workspace/environments/study/StudyTypes";

interface StudyContextPanelProps {
  concept: StudyConcept;
}

export function StudyContextPanel({ concept }: StudyContextPanelProps) {
  return (
    <div className="flex flex-col gap-8 sticky top-12">
      <div className="flex flex-col gap-2">
        <h4 className="text-[10px] uppercase tracking-widest font-medium text-ink/30">
          Source Document
        </h4>
        <p className="text-sm text-ink/70 font-serif italic">
          {concept.sourceDocument}
        </p>
      </div>

      <div className="flex flex-col gap-2">
        <h4 className="text-[10px] uppercase tracking-widest font-medium text-ink/30">
          Current Concept
        </h4>
        <h2 className="text-lg font-serif text-ink tracking-tight">
          {concept.title}
        </h2>
      </div>

      <div className="flex flex-col gap-3">
        <h4 className="text-[10px] uppercase tracking-widest font-medium text-ink/30">
          Related Concepts
        </h4>
        <ul className="flex flex-col gap-2">
          {concept.relatedConcepts.map(rc => (
            <li key={rc} className="text-sm font-mono text-ink/60">
              {rc}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
