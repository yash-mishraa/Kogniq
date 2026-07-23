"use client";

import type { NotebookHistory } from "@/app/workspace/environments/notebook/NotebookTypes";

interface NotebookNarrativeProps {
  history: NotebookHistory[];
}

export function NotebookNarrative({ history }: NotebookNarrativeProps) {
  if (!history || history.length === 0) return null;

  return (
    <div className="flex flex-col gap-3 py-12 border-b border-ink/10 max-w-2xl">
      {history.map((event, index) => (
        <div key={index} className="flex gap-4 items-baseline text-xs font-serif text-ink/40">
          <span className="font-mono uppercase tracking-widest opacity-50 min-w-[100px]">
            {event.timestamp}
          </span>
          <span className="italic">
            {event.description}
          </span>
        </div>
      ))}
    </div>
  );
}
