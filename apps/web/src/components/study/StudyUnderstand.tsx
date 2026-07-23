"use client";

import type { UnderstandContent } from "@/app/workspace/environments/study/StudyTypes";

interface StudyUnderstandProps {
  content: UnderstandContent;
}

export function StudyUnderstand({ content }: StudyUnderstandProps) {
  return (
    <div className="flex flex-col gap-12 text-ink">
      <section className="flex flex-col gap-4">
        <h3 className="text-sm font-mono uppercase tracking-widest text-ink/40">Intuition</h3>
        <p className="text-xl font-serif leading-relaxed text-ink/90">
          {content.intuition}
        </p>
      </section>

      <section className="flex flex-col gap-4">
        <h3 className="text-sm font-mono uppercase tracking-widest text-ink/40">Why It Matters</h3>
        <p className="text-xl font-serif leading-relaxed text-ink/90">
          {content.whyItMatters}
        </p>
      </section>

      <section className="flex flex-col gap-4">
        <h3 className="text-sm font-mono uppercase tracking-widest text-ink/40">Key Takeaways</h3>
        <ul className="flex flex-col gap-4">
          {content.keyTakeaways.map((takeaway, i) => (
            <li key={i} className="flex gap-4 items-start">
              <span className="text-ink/30 mt-1.5 text-xs">■</span>
              <span className="text-lg font-serif leading-relaxed text-ink/80">{takeaway}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
