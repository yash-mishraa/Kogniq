/**
 * Presentation-only translations for the everyday Kogniq experience.
 *
 * The backend state machine, API contracts, and retrieval semantics are
 * untouched. These helpers turn authoritative values into language an
 * ordinary reader can act on; the engineering console keeps the raw values.
 */

import { ApiRequestError, type DocumentSummary, type RagAnswer } from "./api";
import type { StatusTone } from "./format";

export type DocumentPhase = "ready" | "preparing" | "attention" | "unprepared";

export interface DocumentStatusView {
  phase: DocumentPhase;
  label: string;
  tone: StatusTone;
  description: string;
}

const STATUS_VIEWS: Record<DocumentPhase, Omit<DocumentStatusView, "phase">> = {
  ready: {
    label: "Ready to use",
    tone: "success",
    description: "Kogniq can search this document and cite it in answers.",
  },
  preparing: {
    label: "Preparing",
    tone: "accent",
    description: "Kogniq is reading and indexing the file. This can take a few moments.",
  },
  attention: {
    label: "Needs attention",
    tone: "danger",
    description:
      "Preparation did not finish. Your original file is still stored, so you can try again.",
  },
  unprepared: {
    label: "Not prepared yet",
    tone: "warning",
    description: "This file has not been prepared for search yet.",
  },
};

export function documentPhase(doc: Pick<DocumentSummary, "status">): DocumentPhase {
  switch (doc.status.toLowerCase()) {
    case "ready":
      return "ready";
    case "uploaded":
    case "processing":
    case "extracting":
    case "normalizing":
    case "chunking":
    case "embedding":
    case "indexing":
      return "preparing";
    case "failed":
      return "attention";
    case "unindexed":
      return "unprepared";
    default:
      return "unprepared";
  }
}

export function documentStatus(doc: Pick<DocumentSummary, "status">): DocumentStatusView {
  const phase = documentPhase(doc);
  return { phase, ...STATUS_VIEWS[phase] };
}

export interface DocumentBuckets {
  total: number;
  ready: DocumentSummary[];
  preparing: DocumentSummary[];
  attention: DocumentSummary[];
  unprepared: DocumentSummary[];
}

export function documentBuckets(documents: DocumentSummary[]): DocumentBuckets {
  const buckets: DocumentBuckets = {
    total: documents.length,
    ready: [],
    preparing: [],
    attention: [],
    unprepared: [],
  };
  for (const document of documents) {
    buckets[documentPhase(document)].push(document);
  }
  return buckets;
}

export type DocumentActionKind = "ask" | "retry" | "prepare";

export type DocumentActionView =
  | { kind: "ask"; label: string }
  | { kind: "retry"; label: string }
  | { kind: "prepare"; label: string };

/**
 * One clear action per user state. Retry and reindex are separate endpoints
 * but the same server-side operation, so the everyday view never offers both.
 */
export function documentAction(doc: Pick<DocumentSummary, "status">): DocumentActionView | null {
  switch (documentPhase(doc)) {
    case "ready":
      return { kind: "ask", label: "Ask about this" };
    case "attention":
      return { kind: "retry", label: "Try again" };
    case "unprepared":
      return { kind: "prepare", label: "Prepare document" };
    default:
      return null;
  }
}

export interface QueryStatusView {
  label: string;
  tone: StatusTone;
}

export function queryStatus(status: string): QueryStatusView {
  switch (status.toLowerCase()) {
    case "answered":
      return { label: "Answered", tone: "success" };
    case "insufficient_evidence":
      return { label: "Not enough evidence", tone: "warning" };
    case "error":
      return { label: "Couldn't answer", tone: "danger" };
    default:
      return { label: status.replaceAll("_", " "), tone: "neutral" };
  }
}

export interface AnswerOutcome {
  label: string;
  tone: "success" | "warning" | "danger";
  message: string | null;
}

export function answerOutcome(answer: RagAnswer): AnswerOutcome {
  if (answer.status === "error") {
    return {
      label: "Answer unavailable",
      tone: "danger",
      message:
        "Kogniq reached your documents but could not finish writing an answer. Try again in a moment.",
    };
  }
  if (answer.status === "insufficient_evidence" || !answer.grounded || !answer.citations.length) {
    return {
      label: "Not enough evidence",
      tone: "warning",
      message:
        "I couldn't find enough information in the selected documents to answer that confidently. Try selecting more documents or asking a narrower question.",
    };
  }
  return {
    label: "Supported by your documents",
    tone: "success",
    message: null,
  };
}

export interface FriendlyError {
  message: string;
  detail: string | null;
}

/** Turn transport and validation failures into an actionable sentence. */
export function friendlyErrorMessage(error: unknown): FriendlyError {
  if (!error) return { message: "", detail: null };

  if (error instanceof ApiRequestError) {
    const detail = error.message || null;
    if (error.code === "file_too_large" || error.status === 413) {
      return {
        message: "That file is larger than the 10 MB limit. Choose a smaller file and try again.",
        detail,
      };
    }
    if (error.code === "unsupported_extension") {
      return {
        message: "Kogniq supports PDF, plain text, and Markdown files. Choose one of those formats.",
        detail,
      };
    }
    if (error.status === 401) {
      return { message: "Your session has expired. Sign in again to continue.", detail };
    }
    if (error.status === 403) {
      return { message: "You do not have access to that item in this workspace.", detail };
    }
    if (error.status === 404) {
      return { message: "That item is no longer available. Refresh the page to see the latest state.", detail };
    }
    if (error.status === 429) {
      return { message: "Kogniq is handling too many requests. Wait a moment, then try again.", detail };
    }
    if (error.status >= 500) {
      return {
        message: "Kogniq couldn't complete that request. Your documents are safe. Try again in a moment.",
        detail,
      };
    }
    return { message: "Kogniq couldn't complete that request. Try again.", detail };
  }

  if (error instanceof TypeError) {
    return {
      message: "Kogniq couldn't reach the server. Check your connection, then try again.",
      detail: error.message,
    };
  }

  return {
    message: "Something went wrong while completing that request. Try again.",
    detail: error instanceof Error ? error.message : String(error),
  };
}

const CITATION_PATTERN = /\[(S\d+(?:\s*,\s*S\d+)*)\]/g;

/**
 * Render validated citation labels as in-document links so they resolve to the
 * source cards. Unknown labels are left alone and therefore stay visibly
 * unsupported.
 */
export function linkCitations(answer: string, validSourceIds: Iterable<string>): string {
  const valid = new Set(validSourceIds);
  return answer.replace(CITATION_PATTERN, (match, group: string) => {
    const ids = group
      .split(",")
      .map((item) => item.trim())
      .filter((id) => valid.has(id));
    if (!ids.length) return match;
    return ids.map((id) => `[${id}](#citation-${id})`).join(" ");
  });
}

/**
 * Answers occasionally contain LaTeX. Without a math renderer, showing raw
 * delimiters is worse than showing the expression as code, so normalise the
 * common delimiters into safe code spans/fences before Markdown rendering.
 */
export function prepareAnswerMarkdown(
  answer: string,
  validSourceIds: Iterable<string> = [],
): string {
  return normaliseMath(linkCitations(answer, validSourceIds));
}

function normaliseMath(value: string): string {
  const fenced = value
    .replace(/\$\$([\s\S]+?)\$\$/g, (_match, body: string) => {
      return `\n\n\`\`\`text\n${body.trim()}\n\`\`\`\n\n`;
    })
    .replace(/\\\[([\s\S]+?)\\\]/g, (_match, body: string) => {
      return `\n\n\`\`\`text\n${body.trim()}\n\`\`\`\n\n`;
    });

  const inline = fenced
    .replace(/\\\(([\s\S]+?)\\\)/g, (_match, body: string) => {
      return inlineCode(body);
    })
    .replace(/\$([^$\n]+?)\$/g, (match, body: string) => {
      if (body.trim() !== body) return match;
      return inlineCode(body);
    });

  return inline;
}

function inlineCode(value: string): string {
  const safe = value.trim().replaceAll("`", "'");
  return safe ? `\`${safe}\`` : "";
}
