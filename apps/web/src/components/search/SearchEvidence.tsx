"use client";

import type { SearchEvidence as SearchEvidenceType } from "@/app/workspace/environments/search/SearchTypes";

interface SearchEvidenceProps {
  evidence: SearchEvidenceType;
}

export function SearchEvidence({ evidence }: SearchEvidenceProps) {
  return (
    <div className="flex flex-col gap-2 mt-4">
      <blockquote className="border-l-2 border-ink/10 pl-4 py-1 text-ink/70 font-serif leading-relaxed italic text-lg">
        &quot;{evidence.snippet}&quot;
      </blockquote>
      <div className="flex items-center gap-2 text-xs font-mono text-muted pl-4">
        <span>Found in</span>
        <span className="text-ink/60">{evidence.location}</span>
      </div>
    </div>
  );
}
