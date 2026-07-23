"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useKnowledge } from "@/app/workspace/environments/knowledge/KnowledgeContext";
import type { KnowledgeConcept, KnowledgeRelationship, KnowledgeEvidence } from "@/app/workspace/environments/knowledge/KnowledgeTypes";

export function KnowledgeInspector() {
  const { state, dispatch } = useKnowledge();
  const { graph, activeConceptId } = state;

  if (!graph || !graph.data) return null;

  const concept = activeConceptId ? graph.data.concepts.find((c: KnowledgeConcept) => c.id === activeConceptId) : null;

  return (
    <AnimatePresence>
      {concept && (
        <motion.div
          key={concept.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="absolute right-0 top-0 bottom-0 w-[420px] bg-[#fafafa] border-l border-black/5 p-12 overflow-y-auto z-10"
        >
          <div className="flex flex-col gap-12">
            
            {/* Header / Explanation */}
            <div className="flex flex-col gap-4">
              <h2 className="text-3xl font-serif text-ink tracking-tight leading-snug">
                {concept.label}
              </h2>
              <p className="text-lg text-ink/80 leading-relaxed font-serif">
                {concept.explanation}
              </p>
            </div>

            {/* Relationships */}
            <div className="flex flex-col gap-4">
              <h3 className="text-[11px] font-mono text-ink/40 uppercase tracking-widest">
                Related Concepts
              </h3>
              <ul className="flex flex-col gap-3">
                {graph.data.relationships
                  .filter((r: KnowledgeRelationship) => r.sourceId === concept.id || r.targetId === concept.id)
                  .map((r: KnowledgeRelationship) => {
                    const relatedId = r.sourceId === concept.id ? r.targetId : r.sourceId;
                    const relatedConcept = graph.data!.concepts.find((c: KnowledgeConcept) => c.id === relatedId);
                    if (!relatedConcept) return null;

                    return (
                      <li key={relatedId}>
                        <button
                          onClick={() => dispatch({ type: "SELECT_CONCEPT", payload: relatedId })}
                          className="text-left font-serif text-ink/70 hover:text-ink text-lg transition-colors flex items-center gap-3 group"
                        >
                          <span className="text-ink/20 group-hover:text-ink/40 transition-colors">—</span>
                          {relatedConcept.label}
                        </button>
                      </li>
                    );
                  })}
              </ul>
            </div>

            {/* Evidence (Reserved Space) */}
            <div className="flex flex-col gap-4">
              <h3 className="text-[11px] font-mono text-ink/40 uppercase tracking-widest">
                Evidence
              </h3>
              <div className="flex flex-col gap-6">
                {graph.data.evidence
                  .filter((e: KnowledgeEvidence) => e.conceptId === concept.id)
                  .map((evidence: KnowledgeEvidence, idx: number) => (
                    <div key={idx} className="flex flex-col gap-3">
                      <div className="text-[11px] font-mono text-ink/40">
                        {evidence.documentId}
                      </div>
                      <blockquote className="border-l-2 border-black/10 pl-4 py-1 text-ink/60 font-serif leading-relaxed italic">
                        &quot;{evidence.snippet}&quot;
                      </blockquote>
                    </div>
                  ))}
                {graph.data.evidence.filter((e: KnowledgeEvidence) => e.conceptId === concept.id).length === 0 && (
                  <div className="text-ink/30 italic text-sm">
                    No direct textual evidence available.
                  </div>
                )}
              </div>
            </div>

          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
