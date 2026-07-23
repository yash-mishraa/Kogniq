"use client";

import { useNotebook, NotebookProvider } from "./NotebookContext";
import { NotebookSurface, NotebookCanvas, NotebookEmptyState, NotebookCollection } from "@/components/notebook";

function NotebookEnvironmentBody() {
  const { state } = useNotebook();

  if (!state.activeNotebookId) {
    return (
      <NotebookSurface>
        <NotebookEmptyState />
      </NotebookSurface>
    );
  }

  const activeNotebook = state.notebooks.find(n => n.id === state.activeNotebookId);

  if (!activeNotebook) return null;

  return (
    <NotebookSurface>
      <div className="flex w-full h-full">
        {/* Left Panel: The Journal Collection */}
        <div className="w-64 flex-shrink-0 pt-12 pr-8 hidden md:block">
          <NotebookCollection activeId={activeNotebook.id} notebooks={state.notebooks} />
        </div>

        {/* Center Canvas: The Notebook Journal Page */}
        <div className="flex-1 flex flex-col relative max-w-4xl pt-12">
          <NotebookCanvas notebook={activeNotebook} />
        </div>
      </div>
    </NotebookSurface>
  );
}

export function NotebookEnvironment() {
  return (
    <NotebookProvider>
      <NotebookEnvironmentBody />
    </NotebookProvider>
  );
}
