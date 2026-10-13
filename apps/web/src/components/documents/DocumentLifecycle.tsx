"use client";

import type { DocumentStatus } from "@/app/workspace/environments/documents/DocumentsTypes";

const LIFECYCLE_STAGES: { status: DocumentStatus; label: string }[] = [
  { status: "Uploaded", label: "Uploaded" },
  { status: "Extracting", label: "Extracting" },
  { status: "Normalizing", label: "Normalizing" },
  { status: "Chunking", label: "Chunking" },
  { status: "Persisted", label: "Persisted" },
  { status: "Ready", label: "Ready" },
];

export function DocumentLifecycle({ status }: { status: DocumentStatus }) {
  const currentIndex = LIFECYCLE_STAGES.findIndex((stage) => stage.status === status);

  if (currentIndex === -1) return null;

  return (
    <div className="flex flex-col gap-1.5 w-full">
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
                {isActive && status !== "Ready" && <span className="ml-1 inline-block animate-pulse">...</span>}
              </span>
              {i < LIFECYCLE_STAGES.length - 1 && (
                <span className={`text-[10px] ${isPast ? "text-ink/20" : "text-ink/5"}`}>
                  /
                </span>
              )}
            </div>
          );
        })}
      </div>
      {status !== "Ready" && (
        <div className="w-full h-[2px] bg-gray-100 overflow-hidden relative">
          <div 
            className="h-full bg-accent transition-all duration-700 ease-in-out relative"
            style={{ width: `${Math.max(2, (currentIndex / (LIFECYCLE_STAGES.length - 1)) * 100)}%` }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse" />
          </div>
        </div>
      )}
    </div>
  );
}
