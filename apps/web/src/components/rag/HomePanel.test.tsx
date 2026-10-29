import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { DocumentSummary, Overview } from "@/lib/rag/api";
import { HomePanel } from "./HomePanel";

const documentsMock = vi.fn<() => Promise<DocumentSummary[]>>();
const overviewMock = vi.fn<() => Promise<Overview>>();

vi.mock("@/lib/rag/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/rag/api")>();
  return {
    ...actual,
    ragApi: {
      ...actual.ragApi,
      documents: () => documentsMock(),
      overview: () => overviewMock(),
      upload: vi.fn(),
    },
  };
});

function document(id: string, title: string, status: string): DocumentSummary {
  return {
    id,
    title,
    source: "upload",
    status,
    importDate: "2026-01-01T00:00:00Z",
    chunk_count: status === "Ready" ? 12 : 0,
    needs_reindex: status !== "Ready",
  };
}

function overview(recentQueries: Overview["recent_queries"] = []): Overview {
  return {
    generated_at: "2026-01-01T00:00:00Z",
    documents: { total: 0, ready: 0, processing: 0, failed: 0, unindexed: 0, chunks: 0 },
    index: {
      provider: "chroma",
      collection: "kogniq",
      vector_count: 0,
      indexed_documents: 0,
      embedding_model: "all-MiniLM-L6-v2",
      embedding_dimensions: 384,
      chunker_config: null,
      metadata: {},
      error: null,
    },
    queries_7d: {
      count: recentQueries.length,
      answered: 0,
      insufficient: 0,
      avg_total_ms: 0,
      avg_retrieval_ms: 0,
      avg_generation_ms: 0,
      citations: 0,
    },
    evaluation_runs: 0,
    recent_queries: recentQueries,
    capabilities: {
      hybrid_retrieval: true,
      fts5: true,
      prompt_cache: false,
      prompt_cache_note: "Not supported.",
    },
  };
}

function renderHome() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return render(<HomePanel onAsk={vi.fn()} onOpenDocuments={vi.fn()} />, { wrapper });
}

describe("HomePanel", () => {
  beforeEach(() => {
    documentsMock.mockReset();
    overviewMock.mockReset();
    overviewMock.mockResolvedValue(overview());
  });

  afterEach(() => {
    cleanup();
  });

  it("invites the first upload when the workspace has no documents", async () => {
    documentsMock.mockResolvedValue([]);
    renderHome();

    expect(await screen.findByText("Start with a document.")).toBeInTheDocument();
    expect(screen.getByText(/Add a PDF, plain-text file, or Markdown file/)).toBeInTheDocument();
    expect(screen.getByText(/Questions you ask will appear here/)).toBeInTheDocument();
  });

  it("reports every real document state in plain language", async () => {
    documentsMock.mockResolvedValue([
      document("a", "Ready file", "Ready"),
      document("b", "Processing file", "Processing"),
      document("c", "Failed file", "Failed"),
      document("d", "Unprepared file", "Unindexed"),
    ]);
    renderHome();

    expect(await screen.findByText("Ready file")).toBeInTheDocument();
    expect(screen.getByText("Processing file")).toBeInTheDocument();
    expect(screen.getByText("Failed file")).toBeInTheDocument();
    expect(screen.getByText("Unprepared file")).toBeInTheDocument();
    expect(screen.getAllByText("Ready to use").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Preparing").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Needs attention").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Not prepared").length).toBeGreaterThan(0);
    expect(screen.getByText("Ask about this")).toBeInTheDocument();
  });

  it("explains that nothing is searchable yet while preparation continues", async () => {
    documentsMock.mockResolvedValue([document("b", "Processing file", "Processing")]);
    renderHome();

    expect(await screen.findByText("Your documents are not ready yet.")).toBeInTheDocument();
    expect(
      screen.getByText(/Kogniq is still preparing them/),
    ).toBeInTheDocument();
    expect(screen.queryByText("Ask about this")).not.toBeInTheDocument();
  });

  it("shows recent questions with plain statuses", async () => {
    documentsMock.mockResolvedValue([document("a", "Ready file", "Ready")]);
    overviewMock.mockResolvedValue(
      overview([
        {
          id: "q1",
          query_text: "What is attention?",
          status: "insufficient_evidence",
          total_ms: 10,
          retrieval_ms: 4,
          generation_ms: 6,
          citation_count: 0,
          citations_valid: false,
          created_at: "2026-01-01T00:00:00Z",
        },
      ]),
    );
    renderHome();

    await waitFor(() => expect(screen.getByText("What is attention?")).toBeInTheDocument());
    expect(screen.getByText("Not enough evidence")).toBeInTheDocument();
  });
});
