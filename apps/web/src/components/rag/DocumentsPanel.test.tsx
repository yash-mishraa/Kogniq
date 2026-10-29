import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import type { ChunkInspection, DocumentSummary } from "@/lib/rag/api";
import { DocumentsPanel } from "./DocumentsPanel";

const documentsMock = vi.fn<() => Promise<DocumentSummary[]>>();
const chunksMock = vi.fn<() => Promise<ChunkInspection>>();

vi.mock("@/lib/rag/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/rag/api")>();
  return {
    ...actual,
    ragApi: {
      ...actual.ragApi,
      documents: () => documentsMock(),
      documentChunks: () => chunksMock(),
      upload: vi.fn(),
      retry: vi.fn(),
      reindex: vi.fn(),
      deleteDocument: vi.fn(),
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
    chunk_count: 0,
    needs_reindex: status !== "Ready",
    error: status === "Failed" ? "extraction failed: no readable text" : null,
  };
}

function inspection(id: string, status: string): ChunkInspection {
  return { document_id: id, status, chunk_count: 0, chunks: [] };
}

function renderPanel() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return render(<DocumentsPanel focus={null} onAsk={vi.fn()} />, { wrapper });
}

describe("DocumentsPanel", () => {
  beforeAll(() => {
    // jsdom implements neither matchMedia nor scrollIntoView.
    window.matchMedia = ((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia;
    Element.prototype.scrollIntoView = vi.fn();
  });

  beforeEach(() => {
    documentsMock.mockReset();
    chunksMock.mockReset();
    chunksMock.mockResolvedValue(inspection("doc", "Unindexed"));
  });

  afterEach(() => {
    cleanup();
  });

  it("shows an honest empty library", async () => {
    documentsMock.mockResolvedValue([]);
    renderPanel();

    expect(await screen.findByText("No documents yet.")).toBeInTheDocument();
    expect(screen.getByText(/Upload a PDF, text, or Markdown file above/)).toBeInTheDocument();
  });

  it("offers one clear action per document state", async () => {
    documentsMock.mockResolvedValue([
      document("a", "Ready file", "Ready"),
      document("b", "Failed file", "Failed"),
      document("c", "Unprepared file", "Unindexed"),
    ]);
    renderPanel();

    expect(await screen.findByText("Ready file")).toBeInTheDocument();
    expect(screen.getByText("Ask about this")).toBeInTheDocument();
    expect(screen.getByText("Try again")).toBeInTheDocument();
    expect(screen.getByText("Prepare document")).toBeInTheDocument();
    expect(screen.queryByText("Reindex")).not.toBeInTheDocument();
    expect(screen.getByText(/could not be prepared/)).toBeInTheDocument();
  });

  it("explains a failed document and keeps the raw error behind disclosure", async () => {
    documentsMock.mockResolvedValue([document("b", "Failed file", "Failed")]);
    chunksMock.mockResolvedValue(inspection("b", "Failed"));
    renderPanel();

    fireEvent.click(await screen.findByText("Failed file"));

    expect(await screen.findByText("This document needs attention")).toBeInTheDocument();
    expect(screen.getAllByText(/Your original file is still stored/).length).toBeGreaterThan(0);
    expect(screen.getByText("Technical details")).toBeInTheDocument();
    expect(screen.getByText(/extraction failed: no readable text/)).toBeInTheDocument();
  });

  it("tells the reader when a document is not prepared yet", async () => {
    documentsMock.mockResolvedValue([document("c", "Unprepared file", "Unindexed")]);
    renderPanel();

    fireEvent.click(await screen.findByText("Unprepared file"));

    expect(await screen.findByText("This document is not prepared yet")).toBeInTheDocument();
    expect(screen.getByText(/No passages are available yet/)).toBeInTheDocument();
  });
});
