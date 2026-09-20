import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { beforeAll } from 'vitest';
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { LearningHubEnvironment } from "./LearningHubEnvironment";
import { serviceProvider } from "@/lib/providers";
import { WorkspaceContext } from "../../WorkspaceContext";
import type { WorkspaceContextValue } from "../../WorkspaceContext";
import type { WorkspaceMemory } from "../../WorkspaceTypes";

const mockWorkspaceContext: WorkspaceContextValue = {
  activeEnvironmentId: "learningHub",
  history: ["learningHub"],
  memory: {},
  switchEnvironment: vi.fn(),
  remember: vi.fn()
};

const renderWithWorkspace = (ui: React.ReactElement) => {
  return render(
    <WorkspaceContext.Provider value={mockWorkspaceContext}>
      {ui}
    </WorkspaceContext.Provider>
  );
};

describe("LearningHubEnvironment", () => {
beforeAll(() => {
  const mockIntersectionObserver = class {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  };
  global.IntersectionObserver = mockIntersectionObserver as unknown as typeof IntersectionObserver;
});
  beforeEach(() => {
    vi.resetAllMocks();
    cleanup();
  });

  it("should render loading state initially", () => {
    const mockList = vi.fn().mockImplementation(() => new Promise(() => {})); // Never resolves
    serviceProvider.getProvider().resources.listResources = mockList;

    renderWithWorkspace(<LearningHubEnvironment />);
    
    expect(screen.getByText("Loading resources...")).toBeInTheDocument();
  });

  it("should render empty state if no resources", async () => {
    serviceProvider.getProvider().resources.listResources = vi.fn().mockResolvedValue([]);

    renderWithWorkspace(<LearningHubEnvironment />);
    
    await waitFor(() => {
      expect(screen.getByText("No Resources Found")).toBeInTheDocument();
    });
  });

  it("should render resource list and handle selection", async () => {
    const mockResources = [
      { id: "r1", title: "Resource 1", resource_type: "document", status: "completed", created_at: "2023-01-01" },
      { id: "r2", title: "Resource 2", resource_type: "video", status: "processing", created_at: "2023-01-02" },
    ];
    serviceProvider.getProvider().resources.listResources = vi.fn().mockResolvedValue(mockResources);
    serviceProvider.getProvider().resources.getResourceSections = vi.fn().mockResolvedValue([{ id: "s1", title: "Section 1", order: 0 }]);
    serviceProvider.getProvider().resources.getResourceChunks = vi.fn().mockResolvedValue([{ id: "c1", section_id: "s1", text: "Chunk content", order: 0 }]);
    serviceProvider.getProvider().resources.getResourceStatistics = vi.fn().mockResolvedValue({ section_count: 1, chunk_count: 1, total_tokens: 100 });

    renderWithWorkspace(<LearningHubEnvironment />);
    
    // Check list rendered
    await waitFor(() => {
      expect(screen.getAllByText("Resource 1").length).toBeGreaterThan(0);
      expect(screen.getByText("Resource 2")).toBeInTheDocument();
    });

    // Select resource
    const h3 = screen.getAllByText("Resource 1")[0];
    fireEvent.click(h3.closest("button")!);

    // Check detail view loading state
    expect(screen.getByText("Loading intelligence details...")).toBeInTheDocument();

    // Check detail view loaded
    await waitFor(() => {
      expect(screen.getByText("Extracted Content")).toBeInTheDocument();
    });

    // Check statistics and content
    expect(screen.getByText("100")).toBeInTheDocument(); // tokens
    expect(screen.getByText("Section 1")).toBeInTheDocument();
    expect(screen.getByText("Chunk content")).toBeInTheDocument();
  });

  it("should handle incremental loading of chunks", async () => {
    const mockResources = [{ id: "r1", title: "Resource 1", resource_type: "document", status: "completed", created_at: "2023-01-01" }];
    serviceProvider.getProvider().resources.listResources = vi.fn().mockResolvedValue(mockResources);
    serviceProvider.getProvider().resources.getResourceSections = vi.fn().mockResolvedValue([{ id: "s1", title: "Section 1", order: 0 }]);
    
    // First page of chunks (limit=100)
    const page1 = Array.from({ length: 100 }).map((_, i) => ({ id: `c${i}`, section_id: "s1", text: `Chunk ${i}`, order: i }));
    const page2 = [{ id: "c100", section_id: "s1", text: "Chunk 100", order: 100 }];
    
    const mockGetChunks = vi.fn()
      .mockResolvedValueOnce(page1)
      .mockResolvedValueOnce(page2);
      
    serviceProvider.getProvider().resources.getResourceChunks = mockGetChunks;
    serviceProvider.getProvider().resources.getResourceStatistics = vi.fn().mockResolvedValue({ section_count: 1, chunk_count: 101, total_tokens: 100 });

    renderWithWorkspace(<LearningHubEnvironment />);
    
    await waitFor(() => expect(screen.getAllByText("Resource 1").length).toBeGreaterThan(0));
    const h3 = screen.getAllByText("Resource 1")[0];
    fireEvent.click(h3.closest("button")!);
    
    await waitFor(() => expect(screen.getByText("Chunk 0")).toBeInTheDocument());
    
    const loadMoreBtn = screen.getByText("Load more chunks");
    expect(loadMoreBtn).toBeInTheDocument();
    
    fireEvent.click(loadMoreBtn);
    
    await waitFor(() => expect(screen.getByText("Chunk 100")).toBeInTheDocument());
    expect(screen.queryByText("Load more chunks")).not.toBeInTheDocument();
    expect(mockGetChunks).toHaveBeenCalledTimes(2);
  });

  it("should handle error state gracefully", async () => {
    serviceProvider.getProvider().resources.listResources = vi.fn().mockRejectedValue(new Error("API Error"));

    renderWithWorkspace(<LearningHubEnvironment />);
    
    await waitFor(() => {
      expect(screen.getByText("Failed to load resources.")).toBeInTheDocument();
    });
  });
});


import { act } from '@testing-library/react';
import { TrackedChunk } from './LearningHubEnvironment';
import type { ResourceChunk } from '@/lib/services/interfaces/IResourceService';

describe("TrackedChunk Strict Ratio and Lifecycle Validation", () => {
  let intersectionCallback: IntersectionObserverCallback;
  let disconnectMock: ReturnType<typeof vi.fn>;
  let observeMock: ReturnType<typeof vi.fn>;
  
  beforeEach(() => {
    vi.useFakeTimers();
    disconnectMock = vi.fn();
    observeMock = vi.fn();
    
    global.IntersectionObserver = class {
      constructor(callback: IntersectionObserverCallback) {
        intersectionCallback = callback;
      }
      observe = observeMock;
      unobserve = vi.fn();
      disconnect = disconnectMock;
    } as unknown as typeof IntersectionObserver;
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
    cleanup();
  });

  const triggerIntersection = (isIntersecting: boolean, ratio: number) => {
    act(() => {
      intersectionCallback([{
        isIntersecting,
        intersectionRatio: ratio,
        boundingClientRect: {} as DOMRectReadOnly,
        intersectionRect: {} as DOMRectReadOnly,
        rootBounds: null,
        target: document.createElement('div'),
        time: Date.now()
      }], {} as IntersectionObserver);
    });
  };

  it("does not trigger onTracked if intersection ratio is < 0.5 (e.g. 0.49 or 0.4999)", () => {
    const onTracked = vi.fn();
    render(<TrackedChunk chunk={{ id: "chunk-1" } as unknown as ResourceChunk} onTracked={onTracked} />);
    
    triggerIntersection(true, 0.49);
    act(() => { vi.advanceTimersByTime(1500); });
    expect(onTracked).not.toHaveBeenCalled();

    triggerIntersection(true, 0.4999);
    act(() => { vi.advanceTimersByTime(1500); });
    expect(onTracked).not.toHaveBeenCalled();
  });

  it("triggers onTracked exactly once if intersection ratio is >= 0.5 (e.g. 0.5, 0.5001, 1.0)", () => {
    const onTracked = vi.fn();
    render(<TrackedChunk chunk={{ id: "chunk-1" } as unknown as ResourceChunk} onTracked={onTracked} />);
    
    // 0.5
    triggerIntersection(true, 0.5);
    act(() => { vi.advanceTimersByTime(1500); });
    expect(onTracked).toHaveBeenCalledTimes(1);
    expect(onTracked).toHaveBeenCalledWith("chunk-1");
    expect(disconnectMock).toHaveBeenCalled();
  });

  it("clears timer if element leaves viewport before 1500ms", () => {
    const onTracked = vi.fn();
    render(<TrackedChunk chunk={{ id: "chunk-1" } as unknown as ResourceChunk} onTracked={onTracked} />);
    
    triggerIntersection(true, 0.6); // Enter
    act(() => { vi.advanceTimersByTime(1000); }); // Wait 1s
    triggerIntersection(false, 0); // Leave
    act(() => { vi.advanceTimersByTime(1000); }); // Wait another 1s
    
    expect(onTracked).not.toHaveBeenCalled(); // 1500ms continuous did not pass
  });

  it("clears timer if element unmounts before 1500ms", () => {
    const onTracked = vi.fn();
    const { unmount } = render(<TrackedChunk chunk={{ id: "chunk-1" } as unknown as ResourceChunk} onTracked={onTracked} />);
    
    triggerIntersection(true, 0.6); // Enter
    act(() => { vi.advanceTimersByTime(1000); }); // Wait 1s
    unmount();
    act(() => { vi.advanceTimersByTime(1000); }); // Wait another 1s
    
    expect(onTracked).not.toHaveBeenCalled();
    expect(disconnectMock).toHaveBeenCalled();
  });
});
