"use client";

import type { DocumentItem } from "@/app/workspace/environments/documents/DocumentsTypes";

export function DocumentMetadata({ document }: { document: DocumentItem }) {
  const metadata = [];

  if (document.pageCount) {
    metadata.push(`${document.pageCount} pages`);
  }
  
  if (document.readingTime) {
    metadata.push(`~${document.readingTime} min read`);
  }

  if (document.chunkCount) {
    metadata.push(`${document.chunkCount} knowledge chunks`);
  }

  if (document.extractedConcepts) {
    metadata.push(`${document.extractedConcepts} concepts`);
  }

  if (metadata.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-x-2 gap-y-1 text-[11.5px] font-mono text-ink/60 tracking-wide">
      {metadata.map((item, i) => (
        <span key={i} className="flex items-center gap-2">
          {item}
          {i < metadata.length - 1 && <span className="text-ink/20 font-serif">/</span>}
        </span>
      ))}
    </div>
  );
}
