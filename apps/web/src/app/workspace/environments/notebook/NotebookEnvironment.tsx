"use client";

import { useNotebook, NotebookProvider } from "./NotebookContext";
import { NotebookSurface, NotebookCanvas, NotebookEmptyState, NotebookCollection } from "@/components/notebook";

import { useEffect } from "react";
import { serviceProvider } from "@/lib/providers";

function NotebookEnvironmentBody() {
  const { state, dispatch } = useNotebook();
  const { notebooks } = state;

  useEffect(() => {
    if (notebooks.status !== "idle") return;
    
    const controller = new AbortController();
    
    async function hydrate() {
      dispatch({ type: "SET_NOTEBOOKS", payload: { ...notebooks, status: "loading" } });
      try {
        const data = await serviceProvider.getProvider().notebooks.getNotebooks(controller.signal);
        dispatch({ type: "SET_NOTEBOOKS", payload: { status: "ready", data, error: null } });
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") return;
        dispatch({ type: "SET_NOTEBOOKS", payload: { status: "error", data: null, error: err as Error } });
      }
    }
    
    hydrate();
    return () => controller.abort();
  }, [notebooks.status, dispatch, notebooks]);

  if (notebooks.status === "loading") {
    return (
      <NotebookSurface>
        <div className="flex-1 flex items-center justify-center h-full">
          <p className="text-secondary text-lg">Preparing notebook...</p>
        </div>
      </NotebookSurface>
    );
  }

  if (notebooks.status === "error") {
    return (
      <NotebookSurface>
        <div className="flex-1 flex items-center justify-center h-full">
          <p className="text-secondary text-lg">Unable to load notebooks right now.</p>
        </div>
      </NotebookSurface>
    );
  }

  if (!notebooks.data || notebooks.data.length === 0 || !state.activeNotebookId) {
    return (
      <NotebookSurface>
        <NotebookEmptyState />
      </NotebookSurface>
    );
  }

  const activeNotebook = notebooks.data.find(n => n.id === state.activeNotebookId);

  if (!activeNotebook) return null;

  return (
    <NotebookSurface>
      <div className="flex w-full h-full">
        {/* Left Panel: The Journal Collection */}
        <div className="w-64 flex-shrink-0 pt-12 pr-8 hidden md:block">
          <NotebookCollection activeId={activeNotebook.id} notebooks={notebooks.data} />
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
