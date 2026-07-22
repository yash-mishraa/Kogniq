"use client";

import type { DocumentStatus } from "@/app/workspace/environments/documents/DocumentsTypes";

const LIFECYCLE_STAGES: { status: DocumentStatus; label: string }[] = [
  { status: "imported", label: "Imported" },
  { status: "processing", label: "Processing" },
  { status: "chunking", label: "Chunking" },
  { status: "embedding", label: "Embedding" },
  { status: "knowledge-extraction", label: "Extraction" },
  { status: "ready", label: "Ready" },
];

export function DocumentLifecycle({ status }: { status: DocumentStatus }) {
  const currentIndex = LIFECYCLE_STAGES.findIndex((stage) => stage.status === status);

  if (currentIndex === -1) return null;

  return (
    <div className="flex items-center gap-1.5 flex-wrap">
      {LIFECYCLE_STAGES.map((stage, i) => {
        const isPast = i < currentIndex;
        const isActive = i === currentIndex;

        return (
          <div key={stage.status} className="flex items-center gap-1.5">
            <span
              className={`text-[11px] uppercase tracking-widest font-medium transition-colors duration-300 ${
                isActive
                  ? "text-ink font-semibold"
                  : isPast
                  ? "text-ink/30"
                  : "text-ink/10"
              }`}
            >
              {stage.label}
            </span>
            {i < LIFECYCLE_STAGES.length - 1 && (
              <span className={`text-[10px] ${isPast ? "text-ink/20" : "text-ink/5"}`}>
                →
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
