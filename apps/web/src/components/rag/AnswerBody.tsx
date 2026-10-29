"use client";

import Markdown, { type Components } from "react-markdown";
import { prepareAnswerMarkdown } from "@/lib/rag/presentation";

const components: Components = {
  a({ href, children }) {
    if (href?.startsWith("#citation-")) {
      return (
        <a href={href} className="citation-ref">
          {children}
        </a>
      );
    }
    if (href) {
      return (
        <a href={href} target="_blank" rel="noreferrer noopener">
          {children}
        </a>
      );
    }
    return <span>{children}</span>;
  },
};

/**
 * Safe Markdown for generated answers. Raw HTML is skipped, links are
 * constrained, and validated citation labels become in-page anchors that
 * resolve to the real source cards below the answer.
 */
export function AnswerBody({
  answer,
  validSourceIds,
}: {
  answer: string;
  validSourceIds: string[];
}) {
  return (
    <div className="answer-prose">
      <Markdown components={components} skipHtml>
        {prepareAnswerMarkdown(answer, validSourceIds)}
      </Markdown>
    </div>
  );
}
