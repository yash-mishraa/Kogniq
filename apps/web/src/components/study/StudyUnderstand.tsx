"use client";

import type { UnderstandContent } from "@/app/workspace/environments/study/StudyTypes";

import ReactMarkdown from "react-markdown";

interface StudyUnderstandProps {
  content: UnderstandContent;
}

export function StudyUnderstand({ content }: StudyUnderstandProps) {
  if (content.markdown) {
    return (
      <div className="prose prose-lg prose-headings:font-serif prose-headings:font-normal prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-sm prose-h3:font-mono prose-h3:uppercase prose-h3:tracking-widest prose-h3:text-ink/40 prose-p:font-serif prose-p:text-xl prose-p:leading-relaxed prose-p:text-ink/90 prose-li:font-serif prose-li:text-lg prose-li:leading-relaxed prose-li:text-ink/80 text-ink max-w-none">
        <ReactMarkdown>{content.markdown}</ReactMarkdown>
      </div>
    );
  }

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
