"use client";

import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";
import { NotebookEntry } from "./NotebookEntry";
import { NotebookNarrative } from "./NotebookNarrative";
import { motion, AnimatePresence } from "framer-motion";
import { Locus } from "@/components/locus";

interface NotebookCanvasProps {
  notebook: Notebook;
}

export function NotebookCanvas({ notebook }: NotebookCanvasProps) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={notebook.id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col w-full pb-32"
      >
        <NotebookNarrative history={notebook.history} />
        
        <div className="flex flex-col w-full mt-12">
          {notebook.entries.map(entry => (
            <NotebookEntry key={entry.id} entry={entry} />
          ))}
        </div>

        {/* The capture area at the bottom of the notebook */}
        <div className="w-full max-w-2xl mt-16 pt-16 border-t border-ink/5">
          <Locus 
            environmentTitle="Notebook"
            placeholder="│ Capture an idea..."
            mode="free-text"
            onSubmitQuery={() => {
              // In the future this would create an observation/question
              
            }}
          />
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
