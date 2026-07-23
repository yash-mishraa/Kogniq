"use client";

import type { NotebookAnnotation as AnnotationType } from "@/app/workspace/environments/notebook/NotebookTypes";

interface NotebookAnnotationProps {
  annotation: AnnotationType;
}

export function NotebookAnnotation({ annotation }: NotebookAnnotationProps) {
  if (annotation.type !== "marginalia") return null;

  return (
    <div className="text-xs font-serif italic text-ink/40 leading-snug">
      {annotation.content}
    </div>
  );
}
