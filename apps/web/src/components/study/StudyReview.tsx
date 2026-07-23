"use client";

import type { ReviewContent } from "@/app/workspace/environments/study/StudyTypes";

interface StudyReviewProps {
  content: ReviewContent;
}

export function StudyReview({ content }: StudyReviewProps) {
  return (
    <div className="flex flex-col gap-10">
      {content.notes.map((note, index) => (
        <div key={index} className="flex flex-col gap-4">
          <h3 className="text-xl font-serif text-ink tracking-tight border-b border-ink/10 pb-2 inline-block w-fit">
            {note.section}
          </h3>
          <ul className="flex flex-col gap-3 pl-4">
            {note.points.map((point, i) => (
              <li key={i} className="flex gap-4 items-start">
                <span className="text-ink/40 font-serif text-sm mt-0.5">—</span>
                <span className="text-lg font-serif leading-relaxed text-ink/80">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
