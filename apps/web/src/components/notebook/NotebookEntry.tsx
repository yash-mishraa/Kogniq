"use client";

import type { NotebookEntry as EntryType } from "@/app/workspace/environments/notebook/NotebookTypes";
import { NotebookThought } from "./NotebookThought";

interface NotebookEntryProps {
  entry: EntryType;
}

export function NotebookEntry({ entry }: NotebookEntryProps) {
  return (
    <div className="flex flex-col gap-12 w-full pt-16 pb-24 border-b border-ink/5 last:border-0">
      <header className="flex flex-col gap-2 max-w-2xl">
        <h2 className="text-3xl font-serif text-ink tracking-tight leading-snug">
          {entry.title}
        </h2>
        <div className="text-xs font-mono text-ink/30 tracking-widest uppercase">
          {entry.createdAt}
        </div>
      </header>

      <div className="flex flex-col gap-16 w-full">
        {entry.thoughts.map(thought => (
          <NotebookThought key={thought.id} thought={thought} />
        ))}
      </div>
    </div>
  );
}
