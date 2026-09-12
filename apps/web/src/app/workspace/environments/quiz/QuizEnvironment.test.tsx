import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { WorkspaceProvider } from "../../WorkspaceProvider";
import { useWorkspace } from "../../WorkspaceContext";
import { serviceProvider, type IServiceProvider } from "@/lib/providers";
import { QuizEnvironment } from "./QuizEnvironment";

const questions = [{ id: "q1", question: "Question?", options: [{ id: "A" as const, text: "Wrong" }, { id: "B" as const, text: "Right" }, { id: "C" as const, text: "Other" }, { id: "D" as const, text: "Else" }], correctOptionId: "B" as const, explanation: "Right is correct.", difficulty: "easy" as const, tags: [] }];

function Harness() {
  const { remember } = useWorkspace();
  return <><button onClick={() => remember("documents", { openedDocument: "doc-b" })}>Switch document</button><button onClick={() => remember("documents", { openedDocument: undefined })}>Clear document</button><QuizEnvironment /></>;
}

describe("QuizEnvironment", () => {
  beforeEach(() => localStorage.clear());

  afterEach(() => {
    cleanup();
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("loads the active document, locks an answer, and resets when the document clears", async () => {
    const getQuiz = vi.fn().mockResolvedValue(questions);
    vi.spyOn(serviceProvider, "getProvider").mockReturnValue({ quiz: { getQuiz } } as unknown as IServiceProvider);
    render(<WorkspaceProvider initialEnvironmentId="quiz" initialMemory={{ documents: { openedDocument: "doc-a" } }}><Harness /></WorkspaceProvider>);
    await screen.findByText("Question?");
    expect(getQuiz).toHaveBeenCalledWith(expect.objectContaining({ documentId: "doc-a" }));
    fireEvent.click(screen.getByLabelText(/Right/));
    fireEvent.click(screen.getByRole("button", { name: "Check answer" }));
    expect(await screen.findByText("Correct")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Clear document"));
    await waitFor(() => expect(screen.getByText("Choose a document first")).toBeInTheDocument());
  });

  it("loads a new quiz when the selected document changes", async () => {
    const getQuiz = vi.fn().mockResolvedValue(questions);
    vi.spyOn(serviceProvider, "getProvider").mockReturnValue({ quiz: { getQuiz } } as unknown as IServiceProvider);
    render(<WorkspaceProvider initialEnvironmentId="quiz" initialMemory={{ documents: { openedDocument: "doc-a" } }}><Harness /></WorkspaceProvider>);
    await screen.findByText("Question?");
    fireEvent.click(screen.getByText("Switch document"));
    await waitFor(() => expect(getQuiz).toHaveBeenLastCalledWith(expect.objectContaining({ documentId: "doc-b" })));
  });
});
