"use client";

import type { KnowledgeReference } from "@/app/workspace/environments/notebook/NotebookTypes";

interface NotebookConnectionProps {
  reference: KnowledgeReference;
}

export function NotebookConnection({ reference }: NotebookConnectionProps) {
  return (
    <div className="flex flex-col gap-1.5 opacity-40 hover:opacity-100 transition-opacity duration-500 cursor-default">
      <div className="text-[10px] uppercase tracking-widest font-medium text-ink/60">
        Referenced from
      </div>
      <div className="flex flex-col gap-0.5 font-mono text-xs text-ink/80">
        {reference.path.map((segment, index) => (
          <div key={index} className="flex gap-2">
            {index > 0 && <span className="text-ink/30 ml-2">↳</span>}
            <span>{segment}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
