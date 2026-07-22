"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useKnowledge } from "@/app/workspace/environments/knowledge/KnowledgeContext";

export function KnowledgeTrail() {
  const { state, dispatch } = useKnowledge();
  const { trail, graph, activeConceptId } = state;

  if (trail.length === 0 || !graph) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="absolute left-12 top-24 bottom-24 w-[240px] flex flex-col pointer-events-none z-10"
    >
      <div className="text-[11px] font-mono text-ink/40 uppercase tracking-widest mb-8">
        Exploration Trail
      </div>
      
      <div className="flex-1 overflow-y-auto pointer-events-auto flex flex-col gap-6 no-scrollbar">
        <AnimatePresence initial={false}>
          {trail.map((conceptId, index) => {
            const concept = graph.concepts.find(c => c.id === conceptId);
            if (!concept) return null;
            
            const isLast = index === trail.length - 1;
            const isActive = conceptId === activeConceptId;
            
            return (
              <motion.div
                key={`${conceptId}-${index}`}
                layout="position"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="relative flex items-start gap-4"
              >
                {/* Vertical connecting line */}
                {!isLast && (
                  <div className="absolute left-[3px] top-6 bottom-[-24px] w-px bg-black/5" />
                )}
                
                {/* Node indicator */}
                <div className={`mt-2 w-1.5 h-1.5 rounded-full ${isActive ? "bg-ink" : "bg-ink/20"}`} />
                
                <button
                  onClick={() => dispatch({ type: "SELECT_CONCEPT", payload: conceptId })}
                  className={`text-left font-serif transition-colors duration-300 ${
                    isActive ? "text-ink text-lg" : "text-ink/40 text-base hover:text-ink/70"
                  }`}
                >
                  {concept.label}
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
