"use client";

import { useNotebook } from "@/app/workspace/environments/notebook/NotebookContext";
import { Locus } from "@/components/locus";

export function NotebookEmptyState() {
  const { state, dispatch } = useNotebook();

  const handleSelect = () => {
    const defaultId = state.notebooks.data && state.notebooks.data.length > 0
      ? state.notebooks.data[0].id
      : crypto.randomUUID();
      
    dispatch({ type: "SET_ACTIVE_NOTEBOOK", payload: defaultId });
  };

  const suggestions = [
    { label: "Transformer Architecture", detail: "Updated today" },
    { label: "Database Normalization", detail: "Updated 1 week ago" },
  ];

  return (
    <section aria-label="Notebook starting point" className="flex flex-col flex-1 items-start justify-center pb-32 w-full max-w-3xl mx-auto">
      <div className="w-full">
        <Locus 
          environmentTitle="Notebook" 
          placeholder="│ Capture an idea..."
          mode="suggestion"
          suggestions={suggestions}
          onSelect={handleSelect}
          autoFocus 
        />
      </div>
    </section>
  );
}
