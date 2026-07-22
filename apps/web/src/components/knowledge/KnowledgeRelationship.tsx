"use client";

import { motion } from "framer-motion";

export function KnowledgeRelationship({ 
  sourcePos, 
  targetPos, 
  isFaded, 
  isHighlighted 
}: { 
  sourcePos: { x: number; y: number }; 
  targetPos: { x: number; y: number }; 
  isFaded: boolean;
  isHighlighted: boolean;
}) {
  return (
    <motion.line
      x1={`${sourcePos.x}%`}
      y1={`${sourcePos.y}%`}
      x2={`${targetPos.x}%`}
      y2={`${targetPos.y}%`}
      initial={false}
      animate={{
        strokeOpacity: isFaded ? 0.05 : isHighlighted ? 0.2 : 0.1,
        strokeWidth: isHighlighted ? 1.5 : 1,
      }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      stroke="black"
      strokeDasharray="4 6" // Communicates subtle connection rather than rigid edge
    />
  );
}
