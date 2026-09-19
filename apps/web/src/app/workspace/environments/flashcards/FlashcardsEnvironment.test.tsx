import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { FlashcardsEnvironment } from "./FlashcardsEnvironment";
import { serviceProvider } from "@/lib/providers";
import { Mock, vi } from "vitest";
import { WorkspaceProvider } from "../../WorkspaceProvider";

vi.mock("react-markdown", () => ({ default: (props: { children: React.ReactNode }) => <div data-testid="markdown-mock">{props.children}</div> }));

describe("FlashcardsEnvironment", () => {
  let mockEnqueueBatchEvent: Mock;
  let mockGetFlashcards: Mock;
  
  beforeEach(() => {
    vi.resetAllMocks();
    mockEnqueueBatchEvent = vi.fn();
    mockGetFlashcards = vi.fn().mockResolvedValue([
      { id: "c1", question: "Front 1", answer: "Back 1" }
    ]);
    
    (serviceProvider.getProvider as unknown as Mock) = vi.fn().mockReturnValue({
      analytics: {
        enqueueBatchEvent: mockEnqueueBatchEvent,
        initializeDeliveryQueue: vi.fn()
      },
      flashcards: {
        getFlashcards: mockGetFlashcards
      }
    });
  });
  
  it("enqueues flashcard_reviewed event when a card is realistically reviewed", async () => {
    render(
      <WorkspaceProvider initialEnvironmentId="flashcards" initialMemory={{ documents: { openedDocument: "doc-1" } }}>
        <FlashcardsEnvironment />
      </WorkspaceProvider>
    );
    
    // Wait for card to load
    await screen.findByText("Front 1");
    
    // Click the card to flip it
    fireEvent.click(screen.getByText("Front 1"));
    
    // The answer "Back 1" should appear
    await screen.findByText("Back 1");
    
    // The "Easy" button should now be visible, click it
    fireEvent.click(screen.getByText("Easy"));
    
    // Assert the analytics event
    expect(mockEnqueueBatchEvent).toHaveBeenCalledWith(expect.objectContaining({
      event_type: "flashcard_reviewed",
      resource_id: "doc-1",
      data: { card_id: "c1", difficulty: "easy" }
    }));
  });
});
