"use client";

import { useKnowledge } from "@/app/workspace/environments/knowledge/KnowledgeContext";
import { KnowledgeNode } from "./KnowledgeNode";
import { KnowledgeRelationship } from "./KnowledgeRelationship";
import { useMemo } from "react";
import { motion } from "framer-motion";

import type { KnowledgeConcept, KnowledgeRelationship as KnowledgeRelationshipType } from "@/app/workspace/environments/knowledge/KnowledgeTypes";

// Hardcoded intentional, editorial positions for the canonical knowledge graph
// In a real app, this would be computed via an intentional layout algorithm (e.g., hierarchical or semantic clustering) rather than force simulation.
const KNOWLEDGE_LAYOUT: Record<string, { x: number; y: number }> = {
  "transformer": { x: 50, y: 15 },
  
  "encoder": { x: 30, y: 35 },
  "decoder": { x: 70, y: 35 },

  "self-attention": { x: 50, y: 55 },
  
  "multi-head-attention": { x: 50, y: 70 },
  "attention-weights": { x: 50, y: 85 },

  "residual-connection": { x: 20, y: 65 },
  "layer-normalization": { x: 30, y: 80 },
  
  "positional-encoding": { x: 80, y: 20 },
  "feed-forward-network": { x: 80, y: 65 },
};

export function KnowledgeMap() {
  const { state } = useKnowledge();
  const { graph, activeConceptId } = state;

  // Compute active region (active node + immediate neighbors) to fade unrelated regions
  const activeRegionIds = useMemo(() => {
    if (!activeConceptId || !graph.data) return new Set<string>();
    
    const ids = new Set<string>([activeConceptId]);
    graph.data.relationships.forEach((r: KnowledgeRelationshipType) => {
      if (r.sourceId === activeConceptId) ids.add(r.targetId);
      if (r.targetId === activeConceptId) ids.add(r.sourceId);
    });
    
    return ids;
  }, [graph, activeConceptId]);

  if (!graph.data) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      <div className="relative w-full h-full max-w-[1200px] mx-auto pointer-events-auto">
        
        {/* SVG layer for subtle relationship edges */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {graph.data.relationships.map((rel: KnowledgeRelationshipType, idx: number) => {
            const sourcePos = KNOWLEDGE_LAYOUT[rel.sourceId];
            const targetPos = KNOWLEDGE_LAYOUT[rel.targetId];
            if (!sourcePos || !targetPos) return null;

            const isFaded = activeConceptId && !activeRegionIds.has(rel.sourceId) && !activeRegionIds.has(rel.targetId);
            const isHighlighted = activeConceptId && (rel.sourceId === activeConceptId || rel.targetId === activeConceptId);

            return (
              <KnowledgeRelationship 
                key={idx}
                sourcePos={sourcePos}
                targetPos={targetPos}
                isFaded={!!isFaded}
                isHighlighted={!!isHighlighted}
              />
            );
          })}
        </svg>

        {/* Nodes layer */}
        {graph.data.concepts.map((concept: KnowledgeConcept) => {
          const pos = KNOWLEDGE_LAYOUT[concept.id];
          if (!pos) return null;

          const isSelected = concept.id === activeConceptId;
          const isFaded = activeConceptId && !activeRegionIds.has(concept.id);

          return (
            <motion.div
              key={concept.id}
              initial={false}
              animate={{
                opacity: isFaded ? 0.15 : 1,
                scale: isSelected ? 1.05 : 1,
              }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="absolute transform -translate-x-1/2 -translate-y-1/2"
              style={{
                left: `${pos.x}%`,
                top: `${pos.y}%`,
              }}
            >
              <KnowledgeNode 
                concept={concept} 
                isSelected={isSelected} 
              />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
