import { describe, expect, it } from "vitest";
import { ApiRequestError, type DocumentSummary, type RagAnswer } from "./api";
import {
  answerOutcome,
  documentAction,
  documentBuckets,
  documentPhase,
  documentStatus,
  friendlyErrorMessage,
  linkCitations,
  prepareAnswerMarkdown,
  queryStatus,
} from "./presentation";

function document(id: string, status: string): DocumentSummary {
  return {
    id,
    title: `Document ${id}`,
    source: "upload",
    status,
    importDate: "2026-01-01T00:00:00Z",
    chunk_count: 0,
    needs_reindex: status === "Unindexed" || status === "Failed",
  };
}

function answer(overrides: Partial<RagAnswer> = {}): RagAnswer {
  return {
    status: "answered",
    query: "What is this?",
    answer: "A grounded answer.",
    grounded: true,
    citations: [],
    sources: [],
    warnings: [],
    strategy: "hybrid_rrf",
    timings: { retrieval_ms: 1, generation_ms: 1, total_ms: 2 },
    usage: {},
    cache_status: "not_supported",
    ...overrides,
  };
}

describe("everyday presentation", () => {
  it("maps every authoritative document state to a plain phase", () => {
    expect(documentPhase(document("a", "Ready"))).toBe("ready");
    expect(documentPhase(document("b", "Uploaded"))).toBe("preparing");
    expect(documentPhase(document("c", "Processing"))).toBe("preparing");
    expect(documentPhase(document("d", "Extracting"))).toBe("preparing");
    expect(documentPhase(document("e", "Failed"))).toBe("attention");
    expect(documentPhase(document("f", "Unindexed"))).toBe("unprepared");
  });

  it("uses honest everyday labels without changing the backend value", () => {
    expect(documentStatus(document("a", "Ready"))).toMatchObject({
      label: "Ready to use",
      tone: "success",
    });
    expect(documentStatus(document("b", "Processing"))).toMatchObject({
      label: "Preparing",
      tone: "accent",
    });
    expect(documentStatus(document("c", "Failed"))).toMatchObject({
      label: "Needs attention",
      tone: "danger",
    });
    expect(documentStatus(document("d", "Unindexed"))).toMatchObject({
      label: "Not prepared yet",
      tone: "warning",
    });
  });

  it("groups real documents into actionable buckets", () => {
    const buckets = documentBuckets([
      document("a", "Ready"),
      document("b", "Processing"),
      document("c", "Failed"),
      document("d", "Unindexed"),
      document("e", "Ready"),
    ]);
    expect(buckets.total).toBe(5);
    expect(buckets.ready.map((item) => item.id)).toEqual(["a", "e"]);
    expect(buckets.preparing.map((item) => item.id)).toEqual(["b"]);
    expect(buckets.attention.map((item) => item.id)).toEqual(["c"]);
    expect(buckets.unprepared.map((item) => item.id)).toEqual(["d"]);
  });

  it("offers one clear action per user state", () => {
    expect(documentAction(document("a", "Ready"))).toEqual({ kind: "ask", label: "Ask about this" });
    expect(documentAction(document("b", "Processing"))).toBeNull();
    expect(documentAction(document("c", "Failed"))).toEqual({ kind: "retry", label: "Try again" });
    expect(documentAction(document("d", "Unindexed"))).toEqual({
      kind: "prepare",
      label: "Prepare document",
    });
  });

  it("translates query statuses for recent activity", () => {
    expect(queryStatus("answered")).toEqual({ label: "Answered", tone: "success" });
    expect(queryStatus("insufficient_evidence")).toEqual({
      label: "Not enough evidence",
      tone: "warning",
    });
    expect(queryStatus("error")).toEqual({ label: "Couldn't answer", tone: "danger" });
  });

  it("does not present an uncited answer as grounded", () => {
    expect(answerOutcome(answer())).toMatchObject({ label: "Not enough evidence", tone: "warning" });
    expect(
      answerOutcome(
        answer({
          citations: [
            {
              source_id: "S1",
              chunk_id: "c1",
              document_id: "d1",
              document_title: "Doc",
              excerpt: "Evidence",
            },
          ],
        }),
      ),
    ).toMatchObject({ label: "Supported by your documents", tone: "success" });
    expect(answerOutcome(answer({ status: "error", grounded: false }))).toMatchObject({
      label: "Answer unavailable",
      tone: "danger",
    });
  });

  it("turns transport failures into actionable language while keeping detail", () => {
    const tooLarge = friendlyErrorMessage(
      new ApiRequestError("File size exceeds maximum allowed", 400, "file_too_large"),
    );
    expect(tooLarge.message).toContain("10 MB");
    expect(tooLarge.detail).toBe("File size exceeds maximum allowed");

    const expired = friendlyErrorMessage(new ApiRequestError("Unauthorized", 401));
    expect(expired.message).toContain("session has expired");

    const offline = friendlyErrorMessage(new TypeError("Failed to fetch"));
    expect(offline.message).toContain("couldn't reach the server");
  });

  it("links only validated citation labels", () => {
    const linked = linkCitations("First [S1], second [S1, S2], unknown [S9].", ["S1", "S2"]);
    expect(linked).toContain("[S1](#citation-S1)");
    expect(linked).toContain("[S2](#citation-S2)");
    expect(linked).toContain("[S9]");
  });

  it("removes raw LaTeX delimiters without unsafe HTML", () => {
    const markdown = prepareAnswerMarkdown("Inline $E = mc^2$ and $$\\int x\\,dx$$.");
    expect(markdown).toContain("`E = mc^2`");
    expect(markdown).toContain("```text");
    expect(markdown).not.toContain("$$");
    expect(markdown).not.toContain("$E");
  });

  it("leaves currency and malformed delimiters alone", () => {
    expect(prepareAnswerMarkdown("It costs $5 and $10.")).toBe("It costs $5 and $10.");
  });
});
