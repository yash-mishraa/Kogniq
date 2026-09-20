import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { RecommendationsList } from "./RecommendationsList";
import { serviceProvider } from "@/lib/providers";
import { WorkspaceContext } from "../../WorkspaceContext";
import type { WorkspaceContextValue } from "../../WorkspaceContext";

const mockSwitchEnvironment = vi.fn();
const mockRemember = vi.fn();

const mockWorkspaceContext: WorkspaceContextValue = {
  activeEnvironmentId: "learningHub",
  history: ["learningHub"],
  memory: {},
  switchEnvironment: mockSwitchEnvironment,
  remember: mockRemember
};

const renderWithWorkspace = (ui: React.ReactElement) => {
  return render(
    <WorkspaceContext.Provider value={mockWorkspaceContext}>
      {ui}
    </WorkspaceContext.Provider>
  );
};

describe("RecommendationsList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    cleanup();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("should render loading state initially", async () => {
    serviceProvider.getProvider().student.getRecommendations = vi.fn().mockImplementation(() => new Promise(() => {}));

    renderWithWorkspace(<RecommendationsList />);
    
    expect(screen.getByText("Up Next For You")).toBeInTheDocument();
  });

  it("should render empty state if no recommendations", async () => {
    serviceProvider.getProvider().student.getRecommendations = vi.fn().mockResolvedValue({ recommendations: [] });

    renderWithWorkspace(<RecommendationsList />);
    
    await waitFor(() => {
      expect(screen.getByText("You're all caught up! No active recommendations at the moment.")).toBeInTheDocument();
    });
  });

  it("should render error state if API fails", async () => {
    serviceProvider.getProvider().student.getRecommendations = vi.fn().mockRejectedValue(new Error("API failure"));

    renderWithWorkspace(<RecommendationsList />);
    
    await waitFor(() => {
      expect(screen.getByText("Unable to load recommendations")).toBeInTheDocument();
    });
  });

  it("should render recommendations and navigate correctly", async () => {
    serviceProvider.getProvider().student.getRecommendations = vi.fn().mockResolvedValue({
      recommendations: [
        {
          resource_id: "doc-1",
          resource_title: "Overdue Doc",
          action_type: "overdue_review",
          priority_score: 105,
          reason: "Overdue by 5 days"
        },
        {
          resource_id: "doc-2",
          resource_title: "New Doc",
          action_type: "new_resource",
          priority_score: 10,
          reason: "Never studied"
        }
      ]
    });

    renderWithWorkspace(<RecommendationsList />);
    
    await waitFor(() => {
      expect(screen.getByText("Overdue Doc")).toBeInTheDocument();
      expect(screen.getByText("New Doc")).toBeInTheDocument();
    });

    const startButtons = screen.getAllByRole("button");
    expect(startButtons.length).toBe(2);

    // Click first one (overdue_review -> study workspace)
    fireEvent.click(startButtons[0]);
    expect(mockRemember).toHaveBeenCalledWith("documents", { openedDocument: "doc-1" });
    expect(mockSwitchEnvironment).toHaveBeenCalledWith("study");

    // Click second one (new_resource -> documents workspace)
    fireEvent.click(startButtons[1]);
    expect(mockRemember).toHaveBeenCalledWith("documents", { openedDocument: "doc-2" });
    expect(mockSwitchEnvironment).toHaveBeenCalledWith("documents");
  });
});
