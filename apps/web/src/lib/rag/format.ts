/** Presentation helpers shared by the RAG console panels. */

export function formatMs(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  if (value < 1) return "<1 ms";
  if (value < 1000) return `${Math.round(value)} ms`;
  return `${(value / 1000).toFixed(2)} s`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${(value * 100).toFixed(1)}%`;
}

export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toFixed(4);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(2)} MB`;
}

export type StatusTone = "neutral" | "accent" | "success" | "warning" | "danger";

export function statusTone(status: string): StatusTone {
  switch (status.toLowerCase()) {
    case "ready":
    case "completed":
    case "answered":
      return "success";
    case "processing":
    case "uploaded":
    case "extracting":
    case "normalizing":
    case "chunking":
      return "accent";
    case "unindexed":
    case "insufficient_evidence":
      return "warning";
    case "failed":
    case "error":
      return "danger";
    default:
      return "neutral";
  }
}

/** Split an answer into text and citation tokens for inline rendering. */
export type AnswerToken =
  | { type: "text"; value: string }
  | { type: "citation"; value: string };

export function tokenizeAnswer(answer: string): AnswerToken[] {
  const tokens: AnswerToken[] = [];
  const pattern = /\[S\d+(?:\s*,\s*S\d+)*\]/g;
  let cursor = 0;
  for (const match of answer.matchAll(pattern)) {
    const index = match.index ?? 0;
    if (index > cursor) {
      tokens.push({ type: "text", value: answer.slice(cursor, index) });
    }
    tokens.push({ type: "citation", value: match[0] });
    cursor = index + match[0].length;
  }
  if (cursor < answer.length) {
    tokens.push({ type: "text", value: answer.slice(cursor) });
  }
  return tokens;
}

/** Parse a comma-separated keyword field without inventing empty entries. */
export function parseList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
