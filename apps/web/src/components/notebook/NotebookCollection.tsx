"use client";

import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";
import { useNotebook } from "@/app/workspace/environments/notebook/NotebookContext";
import { motion } from "framer-motion";

interface NotebookCollectionProps {
  activeId: string;
  notebooks: Notebook[];
}

export function NotebookCollection({ activeId, notebooks }: NotebookCollectionProps) {
  const { dispatch } = useNotebook();

  return (
    <div className="flex flex-col gap-8 sticky top-12">
      <h4 className="text-[10px] uppercase tracking-widest font-medium text-ink/30">
        Research Journals
      </h4>
      <ul className="flex flex-col gap-6">
        {notebooks.map(notebook => {
          const isActive = notebook.id === activeId;
          return (
            <li key={notebook.id}>
              <button
                onClick={() => dispatch({ type: "SET_ACTIVE_NOTEBOOK", payload: notebook.id })}
                className={`text-left outline-none transition-colors duration-500 flex flex-col gap-1 relative ${
                  isActive ? "text-ink" : "text-ink/40 hover:text-ink/70"
                }`}
              >
                <span className="font-serif text-lg tracking-tight leading-snug">
                  {notebook.title}
                </span>
                {isActive && (
                  <motion.div
                    layoutId="notebook-active-indicator"
                    className="absolute -left-4 top-1 bottom-1 w-[2px] bg-ink/20"
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  />
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
