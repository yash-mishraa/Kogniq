"use client";

import { useKnowledge } from "@/app/workspace/environments/knowledge/KnowledgeContext";
import { KnowledgeNode } from "./KnowledgeNode";
import { KnowledgeRelationship } from "./KnowledgeRelationship";
import { useMemo } from "react";
import { motion } from "framer-motion";

import type { KnowledgeConcept, KnowledgeRelationship as KnowledgeRelationshipType } from "@/app/workspace/environments/knowledge/KnowledgeTypes";

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

  const conceptLayout = useMemo(() => {
    const layout: Record<string, { x: number; y: number }> = {};
    if (!graph.data || !graph.data.concepts) return layout;

    const count = graph.data.concepts.length;
    const cols = Math.ceil(Math.sqrt(count));
    const spacingX = 80 / (cols || 1);
    const spacingY = 80 / (Math.ceil(count / (cols || 1)) || 1);

    graph.data.concepts.forEach((concept, idx) => {
      const col = idx % cols;
      const row = Math.floor(idx / cols);
      layout[concept.id] = {
        x: 10 + col * spacingX,
        y: 10 + row * spacingY,
      };
    });
    return layout;
  }, [graph]);

  if (!graph.data) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      <div className="relative w-full h-full max-w-[1200px] mx-auto pointer-events-auto">
        
        {/* SVG layer for subtle relationship edges */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {graph.data.relationships.map((rel: KnowledgeRelationshipType, idx: number) => {
            const sourcePos = conceptLayout[rel.sourceId];
            const targetPos = conceptLayout[rel.targetId];
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
          const pos = conceptLayout[concept.id];
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
