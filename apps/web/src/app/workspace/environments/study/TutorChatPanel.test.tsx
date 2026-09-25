import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach, beforeAll } from "vitest";
import { TutorChatPanel } from "./TutorChatPanel";

const mockFetch = vi.fn();

const okResponse = (body: unknown) => ({
  ok: true,
  status: 200,
  json: async () => body,
});

describe("TutorChatPanel", () => {
  beforeAll(() => {
    // jsdom does not implement scrollIntoView.
    Element.prototype.scrollIntoView = vi.fn();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    cleanup();
    vi.stubGlobal("fetch", mockFetch);
    localStorage.setItem("token", "session-token");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it("renders the empty-state prompt before any message", () => {
    render(<TutorChatPanel documentId="doc-1" />);
    expect(screen.getByText("Ask me anything about the current document!")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Ask a question...")).toBeInTheDocument();
  });

  it("sends the conversation to the tutor chat endpoint and renders the reply", async () => {
    mockFetch.mockResolvedValueOnce(
      okResponse({ content: "Attention relates tokens to each other.", tool_events: [] })
    );

    render(<TutorChatPanel documentId="doc-1" />);
    fireEvent.change(screen.getByPlaceholderText("Ask a question..."), {
      target: { value: "What is attention?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("Attention relates tokens to each other.")).toBeInTheDocument();
    });

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/agent/tutor/chat",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
          "Authorization": "Bearer session-token",
        }),
      })
    );
    const requestBody = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(requestBody.document_id).toBe("doc-1");
    expect(requestBody.messages).toEqual([{ role: "user", content: "What is attention?" }]);
    expect(screen.getByText("Attention relates tokens to each other.")).toBeInTheDocument();
  });

  it("renders tool events returned by the backend", async () => {
    mockFetch.mockResolvedValueOnce(
      okResponse({
        content: "Grounded answer.",
        tool_events: ["Searched document for: 'What is attention?'"],
      })
    );

    render(<TutorChatPanel documentId="doc-1" />);
    fireEvent.change(screen.getByPlaceholderText("Ask a question..."), {
      target: { value: "What is attention?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("Searched document for: 'What is attention?'")).toBeInTheDocument();
    });
    expect(screen.getByText("Grounded answer.")).toBeInTheDocument();
  });

  it("shows an error message when the request fails", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: async () => ({}),
    });

    render(<TutorChatPanel documentId="doc-1" />);
    fireEvent.change(screen.getByPlaceholderText("Ask a question..."), {
      target: { value: "Hello" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText(/Failed to send message/)).toBeInTheDocument();
    });
  });

  it("does not submit an empty or whitespace-only message", () => {
    render(<TutorChatPanel documentId="doc-1" />);
    const input = screen.getByPlaceholderText("Ask a question...");

    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(mockFetch).not.toHaveBeenCalled();
    expect(screen.getByText("Ask me anything about the current document!")).toBeInTheDocument();
  });

  it("disables the input and send button while the tutor is thinking", async () => {
    mockFetch.mockImplementationOnce(() => new Promise(() => {}));
    render(<TutorChatPanel documentId="doc-1" />);

    fireEvent.change(screen.getByPlaceholderText("Ask a question..."), {
      target: { value: "What is attention?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("Tutor is thinking...")).toBeInTheDocument();
    });
    expect(screen.getByPlaceholderText("Ask a question...")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });
});
