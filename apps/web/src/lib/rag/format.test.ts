import { describe, expect, it } from "vitest";
import { formatMs, formatPercent, parseList, statusTone, tokenizeAnswer } from "./format";

describe("RAG presentation helpers", () => {
  it("formats latency without pretending missing values are zero", () => {
    expect(formatMs(null)).toBe("—");
    expect(formatMs(0.4)).toBe("<1 ms");
    expect(formatMs(42.6)).toBe("43 ms");
    expect(formatMs(1500)).toBe("1.50 s");
  });

  it("formats rates as percentages", () => {
    expect(formatPercent(0.8125)).toBe("81.3%");
    expect(formatPercent(null)).toBe("—");
  });

  it("maps authoritative statuses to honest tones", () => {
    expect(statusTone("Ready")).toBe("success");
    expect(statusTone("Unindexed")).toBe("warning");
    expect(statusTone("Failed")).toBe("danger");
    expect(statusTone("insufficient_evidence")).toBe("warning");
    expect(statusTone("Processing")).toBe("accent");
    expect(statusTone("mystery")).toBe("neutral");
  });

  it("tokenizes citation labels without rewriting surrounding prose", () => {
    const tokens = tokenizeAnswer("Hybrid search fuses ranks [S1]. It also cites [S2, S3].");
    expect(tokens).toEqual([
      { type: "text", value: "Hybrid search fuses ranks " },
      { type: "citation", value: "[S1]" },
      { type: "text", value: ". It also cites " },
      { type: "citation", value: "[S2, S3]" },
      { type: "text", value: "." },
    ]);
  });

  it("does not invent citation tokens for bracketed prose", () => {
    expect(tokenizeAnswer("See [the appendix] for details.")).toEqual([
      { type: "text", value: "See [the appendix] for details." },
    ]);
  });

  it("parses comma-separated expectations without empty entries", () => {
    expect(parseList(" alpha, , beta ,,")).toEqual(["alpha", "beta"]);
    expect(parseList("   ")).toEqual([]);
  });
});
