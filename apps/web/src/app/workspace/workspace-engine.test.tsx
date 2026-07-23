import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { environmentRegistry, EnvironmentRegistry } from "./environments";
import { WorkspaceEngine } from "./WorkspaceEngine";
import { WorkspaceProvider } from "./WorkspaceProvider";
import { useWorkspace } from "./WorkspaceContext";
import { resolveWorkspaceTransition } from "./WorkspaceMotion";

function WorkspaceProbe() {
  const { activeEnvironmentId, history, memory, remember, switchEnvironment } = useWorkspace();
  return <><output data-testid="active">{activeEnvironmentId}</output><output data-testid="history">{history.join(",")}</output><output data-testid="memory">{memory.documents?.selectedContext ?? ""}</output><button onClick={() => switchEnvironment("search")}>switch</button><button onClick={() => remember("documents", { selectedContext: "Architecture notes", scrollPosition: 120 })}>remember</button></>;
}

describe("Workspace Engine foundation", () => {
  it("registers every metadata-only environment", () => {
    expect(environmentRegistry.listEnvironments().map((environment) => environment.id)).toEqual(["documents", "graph", "knowledge", "search", "studio", "study", "notebook", "flashcards", "quiz", "analytics"]);
    const registry = new EnvironmentRegistry();
    registry.registerEnvironment(environmentRegistry.getEnvironment("documents")!);
    expect(registry.getEnvironment("documents")?.locusPlaceholder).toBe("Import knowledge…");
  });

  it("switches environments while retaining history and memory", () => {
    render(<WorkspaceProvider initialEnvironmentId="documents"><WorkspaceProbe /></WorkspaceProvider>);
    fireEvent.click(screen.getByText("remember"));
    fireEvent.click(screen.getByText("switch"));
    expect(screen.getByTestId("active")).toHaveTextContent("search");
    expect(screen.getByTestId("history")).toHaveTextContent("documents,search");
    expect(screen.getByTestId("memory")).toHaveTextContent("Architecture notes");
  });

  it("restores focus to the contextual Locus", async () => {
    render(<WorkspaceEngine initialEnvironmentId="search" />);
    const locus = screen.getByRole("textbox", { name: "Search: Search your knowledge..." });
    await waitFor(() => expect(locus).toHaveFocus());
  });

  it("uses instant transition timing under reduced motion", () => {
    expect(resolveWorkspaceTransition(true).duration).toBe(0);
    expect(resolveWorkspaceTransition(false).duration).toBeGreaterThan(0);
  });
});
