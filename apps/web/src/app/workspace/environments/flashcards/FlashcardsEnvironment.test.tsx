import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { FlashcardsEnvironment } from "./FlashcardsEnvironment";
import { serviceProvider } from "@/lib/providers";

vi.mock("@/lib/providers", () => ({
  serviceProvider: {
    getProvider: vi.fn(),
  },
}));

vi.mock("react-markdown", () => ({ default: (props: any) => <span>{props.children}</span> }));

// Mock the environment context
vi.mock("./FlashcardsContext", () => ({
  useFlashcards: () => ({
    state: {
      type: "flashcards",
      currentIndex: 0,
      responses: { "c1": "easy" },
      isFlipped: true,
      requestId: "test-req-123",
        cards: [
          { id: "c1", question: "Front 1", answer: "Back 1" }
        ],
      order: [0]
    },
    dispatch: vi.fn()
  }),
  FlashcardsProvider: ({ children }: any) => <div>{children}</div>
}));

vi.mock("@/app/workspace/WorkspaceContext", () => ({
  useWorkspace: () => ({ 
    activeDocumentId: "doc-1",
    memory: {
      documents: {
        openedDocument: "doc-1"
      }
    }
  })
}));

describe("FlashcardsEnvironment", () => {
  let mockEnqueueBatchEvent: any;
  
  beforeEach(() => {
    vi.resetAllMocks();
    mockEnqueueBatchEvent = vi.fn();
    
    const mockProvider = {
      analytics: {
        enqueueBatchEvent: mockEnqueueBatchEvent,
      },
    };
    
    (serviceProvider.getProvider as any).mockReturnValue(mockProvider);
  });
  
  it("enqueues flashcard_reviewed event when a card is reviewed", () => {
    render(<FlashcardsEnvironment />);
    
    
    expect(mockEnqueueBatchEvent).toHaveBeenCalledWith({
      event_id: "test-req-123-c1",
      event_type: "flashcard_reviewed",
      resource_id: "doc-1",
      data: { card_id: "c1", difficulty: "easy" },
      idempotency_key: "test-req-123-c1"
    });
  });
});
