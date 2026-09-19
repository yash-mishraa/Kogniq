import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { StudyNavigator } from "./StudyNavigator";
import { serviceProvider } from "@/lib/providers";
import { useStudy } from "@/app/workspace/environments/study/StudyContext";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";

vi.mock("@/lib/providers", () => ({
  serviceProvider: {
    getProvider: vi.fn(),
  },
}));

vi.mock("@/app/workspace/environments/study/StudyContext", () => ({
  useStudy: vi.fn(),
}));

vi.mock("@/app/workspace/WorkspaceContext", () => ({
  useWorkspace: vi.fn(),
}));

describe("StudyNavigator", () => {
  let mockEnqueueBatchEvent: any;
  let mockDispatch: any;
  
  beforeEach(() => {
    vi.resetAllMocks();
    mockEnqueueBatchEvent = vi.fn();
    mockDispatch = vi.fn();
    
    const mockProvider = {
      analytics: {
        enqueueBatchEvent: mockEnqueueBatchEvent,
      },
    };
    
    (serviceProvider.getProvider as any).mockReturnValue(mockProvider);
    
    (useWorkspace as any).mockReturnValue({
      activeEnvironmentId: "study",
      switchEnvironment: vi.fn(),
      memory: {
        documents: {
          openedDocument: "doc-1"
        }
      }
    });
  });
  
  it("enqueues study_session_completed when Finish is clicked", () => {
    (useStudy as any).mockReturnValue({
      state: {
        isStudying: true,
        completed: false,
        activeMode: "test",
        material: {
          requestId: "study-req-123",
          documentId: "doc-1",
          data: {
            test: [
              { question: "Q1", options: ["A", "B", "C", "D"], answer: "A", explanation: "" }
            ]
          },
          chunks: [{ id: "c1", text: "chunk 1", token_estimate: 5 }],
          currentIndex: 0,
        },
        testIndex: 1
      },
      dispatch: mockDispatch,
    });
    
    render(<StudyNavigator />);
    
    fireEvent.click(screen.getByText("Finish Study Session"));
    
    expect(mockDispatch).toHaveBeenCalledWith({ type: "MARK_COMPLETED" });
    
    expect(mockEnqueueBatchEvent).toHaveBeenCalledWith({
      event_id: "study-req-123",
      event_type: "study_session_completed",
      resource_id: "doc-1",
      data: {
        completed_at: expect.any(String)
      },
      idempotency_key: "study-req-123"
    });
  });
});
